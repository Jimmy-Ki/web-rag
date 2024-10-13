let currentEditId = null;

        async function fetchKnowledgeContent(dir) {
            const response = await fetch(`/api/knowledge/show/${dir}`);
            if (response.ok) {
                const data = await response.json();
                const contentContainer = document.getElementById('knowledge-content');
                contentContainer.innerHTML = ''; // 清空当前条目

                data.data.forEach((item) => {
                    const card = document.createElement('div');
                    card.className = 'bg-white rounded-lg shadow-lg p-4 relative';

                    // 按钮内使用反斜杠转义内容
                    const escapedContent = JSON.stringify(item.content);

                    card.innerHTML = `
                        <div class="absolute top-2 right-2">
                            <button class="mt-2 inline-block px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs" onclick='deleteContent("${item.id}");'>删除</button>
                            <button class="mt-2 inline-block px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs" onclick='showModal(${escapedContent}, "${item.id}");'>查看</button>
                        </div>
                        <div>
                            <div class="flex justify-between items-center">
                                <div class="flex items-center">
                                    <button class="mr-2" title="复制" onclick="copyToClipboard('${item.id}')">
                                        <svg t="1728651331200" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4960" width="16" height="16"><path d="M638.596211 191.936191q30.628116 0 54.62014 13.272183t41.347956 32.66999 26.544367 41.858425 9.188435 39.81655l0 576.829511q0 29.607178-11.740778 53.088734t-30.628116 39.81655-42.368893 25.52343-46.963111 9.188435l-503.322034 0q-19.397807 0-42.368893-11.230309t-42.879362-29.607178-33.180459-42.368893-13.272183-48.494516l0-568.662014q0-21.439681 10.209372-44.410768t26.544367-42.368893 37.774676-32.159521 44.921236-12.761715l515.57328 0zM578.360917 830.021934q26.544367 0 45.431705-18.376869t18.887338-44.921236-18.887338-45.431705-45.431705-18.887338l-382.851446 0q-26.544367 0-45.431705 18.887338t-18.887338 45.431705 18.887338 44.921236 45.431705 18.376869l382.851446 0zM578.360917 574.787637q26.544367 0 45.431705-18.376869t18.887338-44.921236-18.887338-45.431705-45.431705-18.887338l-382.851446 0q-26.544367 0-45.431705 18.887338t-18.887338 45.431705 18.887338 44.921236 45.431705 18.376869l382.851446 0zM759.0668 0q43.900299 0 80.654038 26.033898t63.808574 64.319043 42.368893 82.695912 15.314058 81.164506l0 542.117647q0 21.439681-12.761715 39.306082t-31.138584 30.628116-39.81655 20.418744-39.81655 7.657029l-4.083749 0 0-609.499501q-8.167498-70.444666-43.900299-108.219342t-94.947159-49.004985l-498.217348 0q1.020937-2.041874 1.020937-7.14656 0-20.418744 12.251246-41.858425t32.159521-38.795613 44.410768-28.586241 49.004985-11.230309l423.688933 0z" p-id="4961" fill="#bfbfbf"></path></svg>
                                    </button>
                                    <pre class="text-xs text-gray-600 truncate w-1/2">id: ${item.id}</pre>
                                </div>
                            </div>
                            <p class="text-gray-500 text-sm">更新于: ${new Date(item.update_time).toLocaleDateString()}</p>
                            <p class="text-gray-700 line-clamp-5">${item.content}</p>
                        </div>
                    `;
                    contentContainer.appendChild(card);
                });
            } else {
                console.error('Error fetching knowledge content:', response.status);
            }
        }

        function deleteContent(id) {
            fetch(`/api/knowledge/delete/detail/${id}`, {
                method: 'GET',
            })
               .then(response => response.json())
               .then(data => {
                    alert(data.message);
                    window.location.reload();
                })
               .catch(error => {
                    console.error('Error deleting content:', error);
                    alert('删除失败，请重试。');
                });
        }


        function showModal(content, id) {
            const modal = document.getElementById('my-modal');
            const modalContent = document.getElementById('modal-content');
            const modalEditContent = document.getElementById('modal-edit-content');

            // modalContent.textContent = content;  // 将内容设置到对话框中
            modalEditContent.value = content; // 在文本框中显示当前内容
            currentEditId = id; // 保存当前编辑的 ID

            modal.classList.remove('hidden'); // 显示对话框
        }

        document.getElementById('upload-button').onclick = async function () {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];

            if (!file) {
                alert('请先选择一个文件进行上传！');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            // 显示加载覆盖层
            document.getElementById('loading-overlay').classList.remove('hidden');

            try {
                const response = await fetch(`/api/knowledge/upload/${dir}`, {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(result.message);
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    console.error('上传失败:', response.statusText);
                    alert(`上传失败: ${errorData.message}`);
                }
            } catch (error) {
                console.error('请求错误:', error);
                alert('网络错误，请重试。');
            } finally {
                // 隐藏加载覆盖层
                document.getElementById('loading-overlay').classList.add('hidden');
            }
        };
        function copyToClipboard(id) {
            navigator.clipboard.writeText(id).then(() => {
                // 显示复制成功提示
                const successMessage = document.getElementById('copy-success');
                successMessage.classList.remove('hidden');
                setTimeout(() => successMessage.classList.add('hidden'), 2000); // 2秒后隐藏提示
            }).catch(err => {
                console.error('复制失败:', err);
            });
        }

        // 关闭模态框
        document.getElementById('close-modal').onclick = function () {
            document.getElementById('my-modal').classList.add('hidden');
        };

        // 从URL中提取 name 参数
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name'); // 获取 name 的值

        // 如果有 name 参数，更新面包屑
        if (name) {
            document.getElementById('knowledge-name').textContent = name;
        }

        // 从URL中提取 dir 参数
        const pathSegments = window.location.pathname.split("/");
        const dir = pathSegments[pathSegments.length - 1]; // 假设 dir 在路径的最后一部分

        if (dir) {
            document.addEventListener('DOMContentLoaded', () => fetchKnowledgeContent(dir));
        }

        function clearTextarea() {
            document.getElementById('OrderNotes').value = ''; // 清空文本区
        }

        document.getElementById('save-edit').onclick = function () {
            const editedContent = document.getElementById('modal-edit-content').value;
            console.log('Saving content for ID:', currentEditId);
            console.log('Edited content:', editedContent);

            // Make sure to handle the response from the fetch request
            fetch(`/api/knowledge/update/${currentEditId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: editedContent })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json(); // Assuming the server returns JSON
                })
                .then(data => {
                    console.log('Success:', data);
                    // Close the modal or perform any other UI update if necessary
                    // Then refresh the page
                    window.location.reload();
                })
                .catch((error) => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        };
        // 添加文件上传功能
        document.getElementById('upload-button').onclick = async function () {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0]; // 获取用户选择的文件

            if (!file) {
                alert('请先选择一个文件进行上传！');
                return;
            }

            const formData = new FormData();
            formData.append('file', file); // 将文件添加到 FormData

            try {
                const response = await fetch(`/api/knowledge/upload/${dir}`, {
                    method: 'POST',
                    body: formData, // 发送 FormData
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(result.message); // 提示上传成功信息
                    window.location.reload(); // 刷新页面以更新内容
                } else {
                    const errorData = await response.json();
                    console.error('上传失败:', response.statusText);
                    alert(`上传失败: ${errorData.message}`);
                }
            } catch (error) {
                console.error('请求错误:', error);
                alert('网络错误，请重试。');
            }
        };

        async function fetchKnowledgeList() {
            const response = await fetch('/api/knowledge/list');
            if (response.ok) {
                const data = await response.json();
                const knowledgeListContainer = document.getElementById('knowledge-list-body');
                knowledgeListContainer.innerHTML = ''; // 清空现有条目
                data.data.forEach(item => {
                    const row = document.createElement('tr');
                    row.className = 'hover:bg-gray-100';
                    row.innerHTML = `
                        <td class="py-2 px-4 border-b border-gray-200"><button class="mr-2" title="复制" onclick="copyToClipboard('${item.id}')"><pre>${item.id}</pre></td>
                        <td class="py-2 px-4 border-b border-gray-200">${item.name}</td>
                        <td class="py-2 px-4 border-b border-gray-200">${new Date(item.update_time).toLocaleDateString()}</td>
                        <td class="py-2 px-4 border-b border-gray-200">${item.nums}</td>
                        <td class="py-2 px-4 border-b border-gray-200">
                            <button onclick="redirectToDetail('${item.name}', '${item.id}')" class="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">查看</button>
                            <button onclick="deleteKnowledge('${item.id}')" class="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600">删除</button>
                            <button onclick="goDialog('${item.id}')" class="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600">对话</button>
                        </td>
                    `;
                    knowledgeListContainer.appendChild(row);
                });
            } else {
                console.error('Error fetching knowledge list:', response.status);
            }
        }

        function redirectToDetail(name,uuid) {
            const encodedName = encodeURIComponent(name);
            window.location.href = `/knowledge/detail/${uuid}?name=${encodedName}`;
        }

        function goDialog(id) {
            window.location.href = `/${id}`;
        }

        function deleteKnowledge(id) {
            fetch(`/api/knowledge/delete/${id}`, {
                method: 'GET',
            }).then(response => {
                if (response.ok) {
                    fetchKnowledgeList(); // 刷新知识库列表
                } else {
                    console.error('Error deleting knowledge:', response.status);
                }
            }).catch(error => {
                console.error('Error deleting knowledge:', error);
            });
        }

        function copyToClipboard(id) {
            navigator.clipboard.writeText(id).then(() => {
                const successMessage = document.getElementById('copy-success');
                successMessage.classList.remove('hidden');
                setTimeout(() => successMessage.classList.add('hidden'), 2000); // 2秒后隐藏提示
            }).catch(err => {
                console.error('复制失败:', err);
            });
        }

        // 页面加载后获取知识库列表
        document.addEventListener('DOMContentLoaded', fetchKnowledgeList);

        // 创建按钮点击事件
        document.getElementById('create-btn').addEventListener('click', () => {
            document.getElementById('create-modal').classList.remove('hidden');
        });

        // 创建知识库按钮点击事件
        document.getElementById('create-knowledge-btn').addEventListener('click', () => {
            const newKnowledgeName = document.getElementById('new-knowledge-name').value;
            if (newKnowledgeName) {
                createKnowledge(newKnowledgeName);
            } else {
                alert('请输入知识库名称');
            }
        });

        async function createKnowledge(name) {
            const response = await fetch(`/api/knowledge/create/${name}`, {
                method: 'GET',
            });
            if (response.ok) {
                fetchKnowledgeList(); // 刷新知识库列表
                document.getElementById('create-modal').classList.add('hidden'); // 关闭弹窗
                document.getElementById('new-knowledge-name').value = ''; // 清空输入框
            } else {
                console.error('Error creating knowledge:', response.status);
            }
        }
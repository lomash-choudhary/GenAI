document.addEventListener('DOMContentLoaded', () => {
    const todoInput = document.getElementById('todoInput');
    const addTodoBtn = document.getElementById('addTodoBtn');
    const todoList = document.getElementById('todoList');

    let todos = JSON.parse(localStorage.getItem('todos')) || [];

    const saveTodos = () => {
        localStorage.setItem('todos', JSON.stringify(todos));
    };

    const renderTodos = () => {
        todoList.innerHTML = '';
        todos.forEach((todo, index) => {
            const listItem = document.createElement('li');
            listItem.setAttribute('data-index', index);

            listItem.innerHTML = `
                <span class="todo-text">${todo}</span>
                <input type="text" class="edit-input" value="${todo}">
                <div class="actions">
                    <button class="edit">Edit</button>
                    <button class="save" style="display:none;">Save</button>
                    <button class="delete">Delete</button>
                </div>
            `;
            todoList.appendChild(listItem);
        });
    };

    const addTodo = () => {
        const newTodo = todoInput.value.trim();
        if (newTodo) {
            todos.push(newTodo);
            todoInput.value = '';
            saveTodos();
            renderTodos();
        }
    };

    const deleteTodo = (index) => {
        todos.splice(index, 1);
        saveTodos();
        renderTodos();
    };

    const editTodo = (index, newText) => {
        todos[index] = newText;
        saveTodos();
        renderTodos();
    };

    addTodoBtn.addEventListener('click', addTodo);

    todoInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            addTodo();
        }
    });

    todoList.addEventListener('click', (event) => {
        const target = event.target;
        const listItem = target.closest('li');
        if (!listItem) return;

        const index = parseInt(listItem.getAttribute('data-index'));

        if (target.classList.contains('delete')) {
            deleteTodo(index);
        } else if (target.classList.contains('edit')) {
            listItem.classList.add('editing');
            listItem.querySelector('.todo-text').style.display = 'none';
            listItem.querySelector('.edit-input').style.display = 'block';
            listItem.querySelector('.edit-input').focus();
            target.style.display = 'none'; // Hide Edit button
            listItem.querySelector('.save').style.display = 'inline-block'; // Show Save button
        } else if (target.classList.contains('save')) {
            const newText = listItem.querySelector('.edit-input').value.trim();
            if (newText) {
                editTodo(index, newText);
            }
            listItem.classList.remove('editing');
            listItem.querySelector('.todo-text').style.display = 'block';
            listItem.querySelector('.edit-input').style.display = 'none';
            target.style.display = 'none'; // Hide Save button
            listItem.querySelector('.edit').style.display = 'inline-block'; // Show Edit button
        }
    });

    renderTodos();
});

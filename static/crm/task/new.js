const task_card = document.querySelectorAll('.task_card');
const group_body = document.querySelectorAll('.group_body');

const defaultBgColor = document.querySelector('.main_container').style.backgroundColor;
const defaultCardBgColor = '#ffffff';
let draggedItem, droppedElement, noted_task

const Group1 = {
    dom: document.getElementById('group_body_1'),
    data: {count: 0, elements: []}
}
const Group2 = {
    dom: document.getElementById('group_body_2'),
    data: {count: 0, elements: []}
}


let info_group1 = document.getElementById('info_group_1')
let info_group2 = document.getElementById('info_group_2')

function addDragStartEvent(element) {
    element.addEventListener('dragstart', () => {
        draggedItem = element;
        setTimeout(function () {
            element.style.backgroundColor = 'rgba(0, 0, 0, 0.2)'
        }, 0)
    });
}

function addDragEndEvent(element) {
    element.addEventListener('dragend', function () {
        setTimeout(function () {
            element.style.backgroundColor = defaultCardBgColor;
            draggedItem = null;
            droppedElement.style.backgroundColor = defaultBgColor
        }, 0);
    })
}

function update_info_labels() {
    info_group1.innerHTML = `${Group1.data.count} ta task`
    info_group2.innerHTML = `${Group2.data.count} ta task`
}

function define_groups_tasks() {

    task_card.forEach((one) => {
        let pk = parseInt(one.getAttribute('pk'))
        let obj = tasks_all.find(o => o.id === pk);

        if (one.parentNode.id === "group_body_1") {
            Group1.data.count += 1
            Group1.data.elements.push(obj)
        } else {
            Group2.data.count += 1
            Group2.data.elements.push(obj)
        }
    })
    update_info_labels()
}

function getBeforeGroup(pk) {
    let before_group, result
    result = Group1.data.elements.find(o => o.id === pk);
    before_group = Group1
    if (result === undefined) before_group = Group2
    return before_group
}

function getGroupNumberById(id) {
    if (id === "group_body_1") return 0
    else return 1
}

function removeTask(pk) {
    let before_group = getBeforeGroup(pk)
    let task_object, task_object_index
    task_object = before_group.data.elements.find(o => o.id === pk)
    task_object_index = before_group.data.elements.findIndex(i => i.id === pk);
    before_group.data.count -= 1
    before_group.data.elements.splice(task_object_index, 1)
    document.getElementById(`task_${pk}`).remove();
}

function footerEnterDrag(e) {
    e.preventDefault();
    droppedElement = this
    this.style.boxShadow = '5px 10px 10px #888888'
    this.style.borderRadius = '5px'
}

function footerLeaveDrag(e) {
    this.style.boxShadow = null
    this.style.borderRadius = null
}

function footer_buttons_connections() {
    const delete_task = document.getElementById('task_delete_footer')
    const task_finish = document.getElementById('task_finished_footer')

    delete_task.addEventListener('dragover', function (e) {
        e.preventDefault();
    });
    task_finish.addEventListener('dragover', function (e) {
        e.preventDefault();
    });

    delete_task.addEventListener('dragenter', footerEnterDrag);
    task_finish.addEventListener('dragenter', footerEnterDrag);

    delete_task.addEventListener('dragleave', footerLeaveDrag);
    task_finish.addEventListener('dragleave', footerLeaveDrag);

    delete_task.addEventListener('drop', function (e) {
        let pk = parseInt(draggedItem.getAttribute('pk'))
        let before_group = getBeforeGroup(pk)

        let task = before_group.data.elements.find(o => o.id === pk)

        swal({
            title: "Chindan ham o'chirmoqchimisiz?",
            icon: "warning",
            buttons: ["Yo'q", "Ha"],
        }).then((willDelete) => {
            if (willDelete) {
                $.ajax({
                    type: "POST",
                    url: 'change_task_status/',
                    beforeSend: (xhr, settings) => {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    },
                    data: {
                        task: task.id,
                        status: 3
                    },
                    success: (response) => {
                        removeTask(response.id)
                        update_info_labels()
                        swal(`${response.name} o'chirildi.`, {icon: "success",});
                    }
                });

            }
        });
        this.style.boxShadow = null
        this.style.borderRadius = null
    });

    task_finish.addEventListener('drop', function (e) {
        let pk = parseInt(draggedItem.getAttribute('pk'))
        let before_group = getBeforeGroup(pk)
        let task = before_group.data.elements.find(o => o.id === pk)

        swal({
            title: "Chindan ham yakunlamoqchimisiz?",
            icon: "warning",
            buttons: ["Yo'q", "Ha"],
        }).then((willDelete) => {
            if (willDelete) {
                $.ajax({
                    type: "POST",
                    url: 'change_task_status/',
                    beforeSend: (xhr, settings) => {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    },
                    data: {
                        task: task.id,
                        status: 2
                    },
                    success: (response) => {
                        removeTask(response.id)
                        update_info_labels()
                        swal(`${response.name} bajarildi.`, {icon: "success",});
                    }
                });
            }
        });
        this.style.boxShadow = null
        this.style.borderRadius = null
    });

}

function group_body_connections() {
    for (let i = 0; i < task_card.length; i++) {
        const item = task_card[i];
        addDragStartEvent(item)
        addDragEndEvent(item)
    }

    for (let j = 0; j < group_body.length; j++) {
        const list = group_body[j];

        list.addEventListener('dragover', function (e) {
            e.preventDefault();
        });
        list.addEventListener('dragenter', function (e) {
            e.preventDefault();
            droppedElement = this
            this.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
        });
        list.addEventListener('dragleave', function (e) {
            this.style.backgroundColor = defaultBgColor;
        });
        list.addEventListener('drop', function (e) {
            let pk = parseInt(draggedItem.getAttribute('pk'))

            let before_group = getBeforeGroup(pk)
            if (this.id !== before_group.dom.id) {
                let status = getGroupNumberById(this.id)
                let task = before_group.data.elements.find(o => o.id === pk)
                $.ajax({
                    type: "POST",
                    url: 'change_task_status/',
                    beforeSend: (xhr, settings) => {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    },
                    data: {
                        task: task.id,
                        status: status
                    },
                    success: (response) => {
                        removeTask(response.id)
                        let Group
                        if (response.status === 0) Group = Group1
                        else Group = Group2
                        let object = newTaskobject(response.id, response.name, response.date)
                        Group.dom.append(object)
                        Group.data.count += 1
                        Group.data.elements.push(response)
                        update_info_labels()
                    }
                });
            } else {
                droppedElement.style.backgroundColor = defaultBgColor
            }
        });
    }
}

function newTaskobject(pk, name, date) {
    let div = document.createElement("div");
    div.innerHTML = `<div class="task_date text-super">${date}</div>
                <div class="task_name">${name}</div>`
    div.setAttribute('pk', pk)
    div.draggable = true
    div.classList.add('task_card')
    div.id = `task_${pk}`
    addDragStartEvent(div)
    addDragEndEvent(div)
    return div
}

function getFormData(unindexed_array) {
    var indexed_array = {};

    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}

function updateTask(pk, name, note) {
    let index = tasks_all.findIndex(i => i.id === pk);
    if (index !== -1) {
        tasks_all[index]['name'] = name
        tasks_all[index]['note'] = note
    }
    {
        tasks_all.push({
            "id": pk,
            "name": name,
            "note": note
        })
    }
}

define_groups_tasks()
group_body_connections()
footer_buttons_connections()

$(document).ready(function () {
    $('#new_task_button').on('click', function () {
        $('#newTaskForm')[0].reset();
        $('#new_task_modal').modal('show');
    })

    $("#new_task_modal").on('shown.bs.modal', function () {
        $("#new_task_modal input").first().focus();
    });

    $('#newTaskForm').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'create_task/',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                name: data['form_name'],
                user: currentUser
            },
            success: function (response) {
                let objectt = newTaskobject(response.id, response.name, response.date)
                updateTask(response.id, response.name, response.note)
                Group1.dom.append(objectt)
                Group1.data.count += 1
                Group1.data.elements.push(response)
                update_info_labels()
                $('#new_task_modal').modal('hide');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

    $(document).on('click', '.task_name', function () {
        let pk = parseInt(this.closest(".task_card").getAttribute('pk'))
        noted_task = tasks_all.find(o => o.id === pk);
        $('#task_note_modal').modal('show');
        $('#task_note_modal textarea[name="izoh"]').val(noted_task.note);
    });

    $("#task_note_modal").on('shown.bs.modal', function () {
        $("#task_note_modal textarea").first().focus().select();
    });

    $('#task_note_form').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'note_task/',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                note: data['izoh'],
                task: noted_task.id
            },
            success: function (response) {
                updateTask(response.id, response.name, response.note)
                $('#task_note_modal').modal('hide');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

});
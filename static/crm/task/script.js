const lead_card = document.querySelectorAll('.task_card');
const group_body = document.querySelectorAll('.group_body');

const defaultBgColor = document.querySelector('.main_container').style.backgroundColor;
const defaultCardBgColor = '#ffffff';
let draggedItem = null;
let droppedElement = null;

const Group1 = {
    dom: document.getElementById('group_body_1'),
    data: {count: 0, summa: 0, elements: []}
}
const Group2 = {
    dom: document.getElementById('group_body_2'),
    data: {count: 0, summa: 0, elements: []}
}

let noted_handler = {new_group_number: null, lead: null}
let finishedLead = null
let losedLead = null
let editingLead = null

let info_group1 = document.getElementById('info_group_1')
let info_group2 = document.getElementById('info_group_2')


function thousand_separator(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function define_groups_leads() {

    lead_card.forEach((one) => {
        let pk = parseInt(one.getAttribute('pk'))
        let obj = tasks_all.find(o => o.id === pk);
        switch (one.parentNode.id) {
            case "group_body_1":
                Group1.data.count += 1
                Group1.data.summa += obj.price
                Group1.data.elements.push(obj)
                break
            case "group_body_2":
                Group2.data.count += 1
                Group2.data.summa += obj.price
                Group2.data.elements.push(obj)
                break
        }
    })
    update_info_labels()
}

function addDragStartEvent(element) {
    element.addEventListener('dragstart', () => {
        draggedItem = element;
        setTimeout(element.style.backgroundColor = 'rgba(0, 0, 0, 0.2)', 0)
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
    info_group1.innerHTML = `${Group1.data.count} ta mijoz: $${thousand_separator(Group1.data.summa)}`
    info_group2.innerHTML = `${Group2.data.count} ta mijoz: $${thousand_separator(Group2.data.summa)}`
}

function newLeadobject(pk, name, date, summa, company) {
    let div = document.createElement("div");
    div.innerHTML = `<div class="lead_card-header">
                <div class="lead_name text-super">${name}</div>
                <div class="lead_date text-super">${date}</div>
                </div>
                <div class="lead_card-body">
                <a class="lead_price text-super">${thousand_separator(summa)}</a>
                <div class="lead_note text-super">${company}</div>
                </div>`
    div.setAttribute('pk', pk)
    div.draggable = true
    div.classList.add('lead_card')
    div.id = `lead_${pk}`
    addDragStartEvent(div)
    addDragEndEvent(div)
    return div
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

function getBeforeGroup(pk) {
    let before_group
    let result

    result = Group1.data.elements.find(o => o.id === pk);
    before_group = Group1

    if (result === undefined) {
        result = Group2.data.elements.find(o => o.id === pk);
        before_group = Group2
    }
    if (result === undefined) {
        result = Group3.data.elements.find(o => o.id === pk);
        before_group = Group3
    }
    if (result === undefined) {
        before_group = Group4
    }
    return before_group
}

function getGroupNumberById(id) {
    if (id === "group_body_1") return 1
    else if (id === "group_body_2") return 2
    else if (id === "group_body_3") return 3
    else return 4

}

function group_body_connections() {
    for (let i = 0; i < lead_card.length; i++) {
        const item = lead_card[i];
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
                noted_handler.new_group_number = getGroupNumberById(this.id)
                noted_handler.lead = before_group.data.elements.find(o => o.id === pk)
            } else {
                droppedElement.style.backgroundColor = defaultBgColor
            }
        });
    }
}

function updateLead(pk, name, price, company, address) {
    let index = tasks_all.findIndex(i => i.id === pk);
    if (index !== -1) {
        tasks_all[index]['name'] = name

        tasks_all[index]['price'] = price
        tasks_all[index]['company'] = company
        tasks_all[index]['address'] = address
    }
    {
        tasks_all.push({
            "id": pk,
            "name": name,
            "price": price,
            "company": company,
            "address": address
        })
    }
}

function removeLead(pk) {
    let before_group = getBeforeGroup(pk)
    let lead_object, lead_object_index
    lead_object = before_group.data.elements.find(o => o.id === pk)
    lead_object_index = before_group.data.elements.findIndex(i => i.id === pk);
    before_group.data.summa -= lead_object.price
    before_group.data.count -= 1
    before_group.data.elements.splice(lead_object_index, 1)

    document.getElementById(`lead_${pk}`).remove();

}

function footer_buttons_connections() {
    const lead_loser = document.getElementById('task_delete_footer')
    const lead_woned = document.getElementById('lead_woned_footer')

    lead_loser.addEventListener('dragover', function (e) {
        e.preventDefault();
    });
    lead_woned.addEventListener('dragover', function (e) {
        e.preventDefault();
    });

    lead_loser.addEventListener('dragenter', footerEnterDrag);
    lead_woned.addEventListener('dragenter', footerEnterDrag);

    lead_loser.addEventListener('dragleave', footerLeaveDrag);
    lead_woned.addEventListener('dragleave', footerLeaveDrag);

    lead_loser.addEventListener('drop', function (e) {
        let pk = parseInt(draggedItem.getAttribute('pk'))
        let before_group = getBeforeGroup(pk)
        losedLead = before_group.data.elements.find(o => o.id === pk)
        $('#lead_lose_form')[0].reset();
        $('#lead_lose_modal').modal('show');
        this.style.boxShadow = null
        this.style.borderRadius = null
    });

    lead_woned.addEventListener('drop', function (e) {
        let pk = parseInt(draggedItem.getAttribute('pk'))
        let before_group = getBeforeGroup(pk)
        finishedLead = before_group.data.elements.find(o => o.id === pk)
        $('#lead_finished_form')[0].reset();
        $('#lead_finished_modal').modal('show');
        this.style.boxShadow = null
        this.style.borderRadius = null
    });

}

function getFormData(unindexed_array) {
    var indexed_array = {};

    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
}

function addLeadToGroupAndUpdateLabels(response) {
    let Group
    if (response.status === 0) Group = Group1
    else if (response.status === 1) Group = Group2
    else if (response.status === 2) Group = Group3
    else Group = Group4
    let object = newLeadobject(response.id, response.name, response.date, response.price, response.company)
    updateLead(response.id, response.name, response.price, response.company, response.companyAddress)
    Group.dom.append(object)
    Group.data.count += 1
    Group.data.summa += response.price
    Group.data.elements.push(response)
    update_info_labels()
}

define_groups_leads()
group_body_connections()
footer_buttons_connections()
$(document).ready(function () {

    $('#new_lead_button').on('click', function () {
        $('#newLeadForm')[0].reset();
        $('#new_lead_modal').modal('show');
    })

    $("#new_lead_modal").on('shown.bs.modal', function () {
        $("#new_lead_modal input").first().focus();
    });

    $('#newLeadForm').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'create_lead/',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                name: data['form_name'],
                price: parseInt(data['form_price']),
                company: data['form_campany'],
                address: data['form_address'],
                user: currentUser
            },
            success: function (response) {
                let objectt = newLeadobject(response.id, response.name, response.date, response.price, response.company)
                updateLead(response.id, response.name, response.price, response.company, response.companyAddress)
                Group1.dom.append(objectt)
                Group1.data.count += 1
                Group1.data.summa += response.price
                Group1.data.elements.push(response)
                update_info_labels()
                $('#new_lead_modal').modal('hide');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

    $("#lead_note_modal").on('shown.bs.modal', function () {
        $("#lead_note_modal textarea").first().focus();
        $("#lead_note_form h5").first().html(noted_handler.lead.name)
    });

    $('#lead_note_modal').on('hidden.bs.modal', function () {
        droppedElement.style.backgroundColor = defaultBgColor
    });

    $('#lead_note_form').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        let leadId = noted_handler.lead.id
        let newStatus = noted_handler.new_group_number - 1
        removeLead(leadId)
        $.ajax({
            type: "POST",
            url: 'change_lead_status/',
            beforeSend: (xhr, settings) => {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                izoh: data['izoh'],
                lead: leadId,
                status: newStatus,
                user: currentUser
            },
            success: (response) => {
                addLeadToGroupAndUpdateLabels(response)
                $('#lead_note_modal').modal('hide');
            }
        });
    });

    $("#lead_finished_modal").on('shown.bs.modal', function () {
        $("#lead_finished_modal input").first().focus();
        $("#lead_finished_modal h5").first().html(`Yakunlash. Narx ${finishedLead.price}`)
    });

    $("#lead_lose_modal").on('shown.bs.modal', function () {
        $("#lead_lose_modal textarea").first().focus();
    });

    $("#edit_lead_modal").on('shown.bs.modal', function () {
        $("#edit_lead_modal input").first().focus().select();
    });

    $(document).on('click', '.task_name', function () {
        let pk = parseInt(this.closest(".task_card").getAttribute('pk'))

        editingLead = tasks_all.find(o => o.id === pk);
        $('#edit_lead_modal').modal('show');
        $('#edit_lead_modal input[name="form_name"]').val(editingLead.name);
        $('#edit_lead_modal input[name="form_price"]').val(editingLead.price);
        $('#edit_lead_modal input[name="form_campany"]').val(editingLead.company);
        $('#edit_lead_modal input[name="form_address"]').val(editingLead.address);

    });


});

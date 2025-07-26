const lead_card = document.querySelectorAll('.lead_card');
const group_body = document.querySelectorAll('.group_body');

const defaultBgColor = document.querySelector('.main_container').style.backgroundColor;
const defaultCardBgColor = '#272e48';
let draggedItem = null;
let droppedElement = null;

let Groups = []

let noted_handler = {new_column_pk: null, lead: null}
let finishedLead = null
let losedLead = null
let editingLead = null

function thousand_separator(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function define_groups_leads() {

    lead_card.forEach((one) => {
        let pk = parseInt(one.getAttribute('pk'))
        let obj = leads_all.find(o => o.id === pk);
        for (let i = 0; i < Groups.length; i++) {
            if (one.parentNode.id === Groups[i].dom.id) {
                Groups[i].data.count += 1
                Groups[i].data.summa += obj.price
                Groups[i].data.elements.push(obj)
                break
            }
        }
    })
    update_info_labels()
}

function define_column_groups() {
    for (const column of board_columns) {
        Groups.push(
            {
                dom: document.getElementById(`group_body_${column.id}`),
                data: {count: 0, summa: 0, elements: []}
            }
        )
    }

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
    for (const group of Groups) {
        let pk = 0;
        for (const boardColumn of board_columns) {
            if (group.dom.id === `group_body_${boardColumn.id}`) {
                pk = boardColumn.id;
                break;
            }
        }
        document.getElementById(`info_group_${pk}`).innerHTML = `${group.data.count} ta mijoz: $${thousand_separator(group.data.summa)}`
    }
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
    for (let group of Groups) {
        result = group.data.elements.find(o => o.id === pk);
        before_group = group
        if (result !== undefined) break;
    }
    return before_group
}

function getGroupNumberById(id) {
    for (const column of board_columns) {
        if (`group_body_${column.id}` === id) return column.id;
    }
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
                noted_handler.new_column_pk = getGroupNumberById(this.id)
                noted_handler.lead = before_group.data.elements.find(o => o.id === pk)
                $('#lead_note_form')[0].reset();
                $('#lead_note_modal').modal('show');
            } else {
                droppedElement.style.backgroundColor = defaultBgColor
            }
        });
    }
}

function updateLead(pk, name, price, company, address) {
    let index = leads_all.findIndex(i => i.id === pk);
    if (index !== -1) {
        leads_all[index]['name'] = name
        leads_all[index]['price'] = price
        leads_all[index]['company'] = company
        leads_all[index]['address'] = address
    }
    {
        leads_all.push({
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
    const lead_loser = document.getElementById('lead_losed_footer')
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

    for (let i = 0; i < Groups.length; i++) {
        if (Groups[i].dom.id === `group_body_${response.pole}`) {
            let object = newLeadobject(response.id, response.name, response.date, response.price, response.company)
            updateLead(response.id, response.name, response.price, response.company, response.companyAddress)
            Groups[i].dom.append(object)
            Groups[i].data.count += 1
            Groups[i].data.summa += response.price
            Groups[i].data.elements.push(response)
            break;
        }
    }
    update_info_labels()
}


$(document).ready(function () {
    define_column_groups()
    define_groups_leads()
    group_body_connections()
    footer_buttons_connections()

    $('#new_lead_button').on('click', function () {
        $('#newLeadForm')[0].reset();
        $('#new_lead_modal').modal('show');
    })

    $('#add_pole_btn').on('click', function () {
        $('#add_pole_form')[0].reset();
        $('#add_pole').modal('show');
    })
    $('.edit_pole_pen').on('click', function () {
        let pole_pk = parseInt(this.getAttribute("column_pk"))
        for (const boardColumn of board_columns) {
            if (pole_pk === boardColumn.id) {
                $('#edit_pole_form')[0].reset();
                $('#edit_pole_form input[name="name"]').val(boardColumn.name);
                $('#edit_pole_form input[name="id"]').val(boardColumn.id);
                $('#edit_pole').modal('show');
                break
            }
        }
    })
    $("#edit_pole").on('shown.bs.modal', function () {
        $("#edit_pole input").first().focus().select();
    });
    $("#add_pole").on('shown.bs.modal', function () {
        $("#add_pole input").first().focus();
    });
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
                Groups[0].dom.append(objectt)
                Groups[0].data.count += 1
                Groups[0].data.summa += response.price
                Groups[0].data.elements.push(response)
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
        let newStatus = noted_handler.new_column_pk
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
    $(document).on('click', '.lead_name', function () {
        let pk = parseInt(this.closest(".lead_card").getAttribute('pk'))

        editingLead = leads_all.find(o => o.id === pk);
        $('#edit_lead_modal').modal('show');
        $('#edit_lead_modal input[name="form_name"]').val(editingLead.name);
        $('#edit_lead_modal input[name="form_price"]').val(editingLead.price);
        $('#edit_lead_modal input[name="form_campany"]').val(editingLead.company);
        $('#edit_lead_modal input[name="form_address"]').val(editingLead.address);

    });

    $('#lead_finished_form').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'lead_finished/',
            beforeSend: (xhr, settings) => {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                price: data['price'],
                lead: finishedLead.id,
                user: currentUser
            },
            success: (response) => {
                removeLead(response.id)
                update_info_labels()
                $('#lead_finished_modal').modal('hide');
                finishedLead = null
            }
        });
    });

    $('#lead_lose_form').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'lead_losed/',
            beforeSend: (xhr, settings) => {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                izoh: data['izoh'],
                lead: losedLead.id,
                user: currentUser
            },
            success: (response) => {
                removeLead(response.id)
                update_info_labels()
                $('#lead_lose_modal').modal('hide');
                losedLead = null
            }
        });
    });

    $('#edit_lead_form').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        event.preventDefault();

        $.ajax({
            type: "POST",
            url: 'edit_lead/',
            beforeSend: (xhr, settings) => {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: {
                lead: editingLead.id,
                name: data['form_name'],
                price: parseInt(data['form_price']),
                company: data['form_campany'],
                address: data['form_address'],
                user: currentUser
            },
            success: (response) => {
                removeLead(response.id)
                addLeadToGroupAndUpdateLabels(response)
                $('#edit_lead_modal').modal('hide');
            }
        });
    });
});

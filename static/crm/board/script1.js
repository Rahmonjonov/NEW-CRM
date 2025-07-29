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

function is_B2B() {
    return company_type === "B2B"
}

function ignore_null(value) {
    if (value === null) {
        return ""
    } else {
        return value
    }
}

function get_telefon(phone) {
    phone = phone.replaceAll(" ", "")
    phone = phone.replaceAll("-", "")
    phone = phone.replaceAll("(", "")
    phone = phone.replaceAll(")", "")
    return phone;
}

function check_telefon(phone) {
    phone = get_telefon(phone)
    return phone.length === 9;
}

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

function newLeadobject(pk, name, date, summa, company, phone, created_user, validation, validation_date) {
    let div = document.createElement("div");
    const LANGUAGE_CODE = "{{ LANGUAGE_CODE }}";
    let nameHTML = '';

    if (validation) {
        nameHTML = `<div class="lead_name text-super">${ignore_null(name)}</div>`;
    } else {
        nameHTML = `<div class="lead_name text-super" style="color: red !important;">${ignore_null(name)}</div>`;
    }
    let validityText = "Yaroqlilik muddati";
    let phoneText = "Telefon";

    if (LANGUAGE_CODE === "en") {
        validityText = "Validity period";
        phoneText = "Telephone";
    } else if (LANGUAGE_CODE === "ru") {
        validityText = "Срок действия";
        phoneText = "Телефон";
    }
    div.innerHTML = `
        <div class="lead_card-header">
            ${nameHTML}
            <div class="lead_datediv text-super">
                <div class="lead_date">${date}</div>
                <div class="created">${created_user}</div>
            </div>
        </div>
        <div class="other_lead">
            <div>
                <a class="lead_other_price text-super">
                ${validityText}: ${validation_date ?? ''}
            </a>
            </div>
            <div>
                <a class="lead_other_price text-super">
                ${phoneText}: ${phone}
            </a>
            </div>
        </div>
        <div class="lead_card-body">
            <a class="lead_price text-super">${summa}</a>
            <div class="lead_note text-super">${company}
                <a href="/edit/?id=${pk}"><i class="fa fa-info-circle"></i></a>
            </div>
        </div>
    `
    div.setAttribute('pk', pk)
    div.draggable = true
    div.classList.add('lead_card')
    div.id = `lead_${pk}`
    addDragStartEvent(div)
    addDragEndEvent(div)
    return div
}

function newLeadobjecetttttttttt(pk, name, date, summa, company, phone, created_user) {
    let div = document.createElement("div");
    div.innerHTML = `<div class="lead_card-header">
                <div class="lead_name text-super">${ignore_null(name)}</div>
                <div class="lead_datediv text-super">
                        <div class="lead_date">${date}</div>
                        <div class="created">${created_user}</div>
                </div>
                </div>
                <div class="lead_card-body">
                <a class="lead_price text-super">${thousand_separator(summa)}</a>
                <div class="lead_note text-super">${ignore_null(company)}
                <a href="/edit/?id=${pk}"><i class="fa fa-info-circle"></i></a>
                </div>
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

function updateLead(pk, name, price, company, address, phone) {
    let index = leads_all.findIndex(i => i.id === pk);
    console.log(name)
    console.log(phone)
    if (index !== -1) {
        leads_all[index]['name'] = name;
        leads_all[index]['price'] = price;
        leads_all[index]['company'] = company;
        leads_all[index]['address'] = address;
        leads_all[index]['phone'] = phone;
    } else {
        leads_all.push({
            "id": pk,
            "name": name,
            "price": price,
            "company": company,
            "address": address,
            "phone": phone,
        });
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
    console.log(response)
    for (let i = 0; i < Groups.length; i++) {
        if (Groups[i].dom.id === `group_body_${response.pole}`) {
            let object;
            object = newLeadobject(response.id, response.name, response.date, response.price, response.company, response.phone, response.created_user.username, response.get_validity_period, response.validity_period)
            updateLead(response.id, response.name, response.price, response.company, response.district, response.phone)
            console.log(response.phone)
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
    $('#phone_tel').mask('(000) 00 000 00 00');
    $('#phone_tel_edit').mask('(000) 00 000 00 00');

    $('#new_lead_button').on('click', function () {
        $('#newLeadForm')[0].reset();
        $('#new_lead_modal').modal('show');
    })

    $('#add_pole_btn').on('click', function () {
        $('#add_pole_form')[0].reset();
        $('#add_pole').modal('show');
    })
    $('#import_excel').on('click', function () {
        $('#excelExportForm')[0].reset();
        let excelModal = new bootstrap.Modal(document.getElementById('ExcelExportModal'));
        excelModal.show();
    })
    // $('#excel_export_btn').on('click', function() {
    //     $('#excel_export_form')[0].reset();
    //     $('#ExcelExportModal').modal({
    //         backdrop: 'static',
    //         keyboard: false
    //     }).modal('show');
    // });

    
    $('.edit_pole_pen').on('click', function () {
        let pole_pk = parseInt(this.getAttribute("column_pk"))
        for (const boardColumn of board_columns) {
            if (pole_pk === boardColumn.id) {
                $('#edit_pole_form')[0].reset();
                $('#edit_pole_form input[name="name"]').val(boardColumn.name);
                $('#edit_pole_form input[name="number"]').val(boardColumn.number);
                
                $('#edit_pole_form input[name="id"]').val(boardColumn.id);
                $('#edit_pole').modal('show');
                break
            }
        }
    })
    $('.delete_pole_pen').on('click', function () {
        let pole_pk = parseInt(this.getAttribute("column_pk"))
        for (const boardColumn of board_columns) {
            if (pole_pk === boardColumn.id) {
                swal({
                    title: `${boardColumn.name} maydonini o'chirmoqchimisiz?`,
                    icon: "warning",
                    buttons: ["Yo'q", "Ha"],
                }).then((willDelete) => {
                    if (willDelete) {

                        $.ajax({
                            type: "GET",
                            url: check_can_delete + '?pole_id=' + pole_pk.toString(),
                            beforeSend: (xhr, settings) => {
                                xhr.setRequestHeader("X-CSRFToken", csrf_token);
                            },
                            success: (response) => {
                                if (response.status === 500) {
                                    let text = '';
                                    for (const item of response['data']) {
                                        text += `${item['created_user__username']} da ${item['count']} ta\n`
                                    }
                                    swal(`Bu maydonni o'chirib bo'lmaydi. Chunki bu maydonda ledlar bor.
                                        ${text} ma'lumotlarni boshqa maydonga olib o'tish kerak.
                                        `, {icon: "error",});
                                } else if (response.status === 200) {
                                    $.ajax({
                                        type: "POST",
                                        url: delete_pole,
                                        beforeSend: (xhr, settings) => {
                                            xhr.setRequestHeader("X-CSRFToken", csrf_token);
                                        },
                                        data: {
                                            pole_id: pole_pk
                                        },
                                        success: (response) => {
                                            location.reload();
                                        }
                                    });
                                }
                            }
                        });
                    }
                });
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
    $('#ExcelExportModal').on('shown.bs.modal', function () {
        console.log("Modal to‘liq ochildi");
    })

    $('#newLeadForm').submit(function (event) {
        let data = getFormData($(this).serializeArray())
        console.log(data)
        event.preventDefault();
        let dataBody = {}

        if (is_B2B()) {
            dataBody = {
                name: data['form_name'],
                price: parseInt(data['form_price']),
                company: data['form_campany'],
                address: data['form_address'],
                validity_period: data['validity_period'],
                phone: get_telefon(data['form_phone']),
                referral: data['referral'],
                user: currentUser
            }
        } else {
            dataBody = {
                name: data['form_name'],
                validity_period: data['validity_period'],
                price: parseInt(data['form_price']),
                phone: get_telefon(data['form_phone']),
                referral: data['referral'],
                user: currentUser
            }
        }
        
        $.ajax({
            type: "POST",
            url: 'create_lead/',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
                console.log(dataBody)
            },
            data: dataBody,
            success: function (response) {
                addLeadToGroupAndUpdateLabels(response);
                $('#new_lead_modal').modal('hide');
                console.log('succes')
            },
            error: function (error) {
                console.log(error);
                console.log(dataBody)
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
        console.log(leads_all)
        console.log(editingLead.phone)
        console.log(editingLead.name)
        console.log(editingLead.date)
        $('#edit_lead_modal').modal('show');
        $('#edit_lead_modal input[name="form_name"]').val(editingLead.name);
        $('#edit_lead_modal input[name="form_price"]').val(editingLead.price);
        $('#edit_lead_modal input[name="form_campany"]').val(editingLead.company);
        $('#edit_lead_modal input[name="form_address"]').val(editingLead.address);
        $('#edit_lead_modal input[name="form_phone"]').val(editingLead.phone);
        $('#phone_tel_edit').trigger('input');


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
        let bodyData = {};
        bodyData = {
                lead: editingLead.id,
                name: data['form_name'],
                price: parseInt(data['form_price']),
                company: data['form_campany'],
                address: data['form_address'],
                phone:data['form_phone'],
                user: currentUser
        }
        $.ajax({
            type: "POST",
            url: 'edit_lead/',
            beforeSend: (xhr, settings) => {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            data: bodyData,
            success: (response) => {
                removeLead(response.id)
                addLeadToGroupAndUpdateLabels(response)
                $('#edit_lead_modal').modal('hide');
            }
        });
    });
});



$('#excelExportForm').submit(function(event) {
    event.preventDefault();
    
    let formData = new FormData();
    formData.append('excel_file', $('#excelFile')[0].files[0]);
    formData.append('csrfmiddlewaretoken', csrf_token);
    
    $.ajax({
        url: '/import_leads_from_excel/',  
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        },
        success: function(response) {
            if (response.status === 'success') {
                response.data.forEach(lead => {
                    addLeadToGroupAndUpdateLabels(lead);

                });
                $('#excelExportForm')[0].reset();
                document.getElementById('ExcelExportModal').style.display = 'none';
                document.querySelector('.modal-backdrop').remove();
                document.body.classList.remove('modal-open');
                console.log(response.data.length)
                console.log('aliii')
            } else {
               console.log(response.message)
            }
        },
        error: function(xhr, status, error) {
           console.log(error)
        }
    });
});

console.log(222)
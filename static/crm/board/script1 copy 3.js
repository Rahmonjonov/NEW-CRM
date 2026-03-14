const lead_card = document.querySelectorAll('.lead_card');
const group_body = document.querySelectorAll('.group_body');

const defaultBgColor = document.querySelector('.main_container').style.backgroundColor;
const defaultCardBgColor = '#272e48';
let draggedItem = null;
let droppedElement = null;

let Groups = [];

let noted_handler = { new_column_pk: null, lead: null };
let finishedLead  = null;
let losedLead     = null;
let editingLead   = null;

function is_B2B() { return company_type === "B2B"; }

function ignore_null(value) { return value === null ? "" : value; }

function get_telefon(phone) {
    if (!phone) return "";
    return phone.replaceAll(" ", "").replaceAll("-", "").replaceAll("(", "").replaceAll(")", "");
}

function check_telefon(phone) { return get_telefon(phone).length === 9; }

function thousand_separator(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function startSingleCountdown(timerEl) {
    const deadline = new Date(timerEl.dataset.validity);
    function tick() {
        const diff = deadline - new Date();
        if (diff <= 0) { timerEl.innerText = ""; return; }
        const days    = Math.floor(diff / 86400000);
        const hours   = Math.floor((diff / 3600000) % 24);
        const minutes = Math.floor((diff / 60000) % 60);
        let parts = [];
        if (days > 0)              parts.push(`${days} kun`);
        if (hours > 0 || days > 0) parts.push(`${hours} soat`);
        parts.push(`${minutes} daqiqa`);
        timerEl.innerText = parts.join(' ');
    }
    tick();
    setInterval(tick, 60000);
}

/* ─── Guruh / lead hisoblash ─── */
function define_groups_leads() {
    lead_card.forEach((one) => {
        let pk  = parseInt(one.getAttribute('pk'));
        let obj = leads_all.find(o => o.id === pk);
        for (let i = 0; i < Groups.length; i++) {
            if (one.parentNode && Groups[i].dom) {
                if (one.parentNode.id === Groups[i].dom.id) {
                    Groups[i].data.count  += 0.5;
                    Groups[i].data.summa  += obj ? obj.price : 0;
                    Groups[i].data.elements.push(obj);
                    break;
                }
            }
        }
    });
    update_info_labels();
}

function define_column_groups() {
    for (const column of board_columns) {
        Groups.push({
            dom:  document.getElementById(`group_body_${column.id}`),
            data: { count: 0, summa: 0, elements: [] }
        });
    }
}

function addDragStartEvent(element) {
    element.addEventListener('dragstart', () => {
        draggedItem = element;
        setTimeout(() => element.style.backgroundColor = 'rgba(0,0,0,0.2)', 0);
    });
}

function addDragEndEvent(element) {
    element.addEventListener('dragend', function () {
        setTimeout(function () {
            element.style.backgroundColor = defaultCardBgColor;
            draggedItem = null;
            if (droppedElement) droppedElement.style.backgroundColor = defaultBgColor;
        }, 0);
    });
}

function update_info_labels() {
    for (const group of Groups) {
        let pk = 0;
        for (const boardColumn of board_columns) {
            if (group.dom && group.dom.id === `group_body_${boardColumn.id}`) {
                pk = boardColumn.id; break;
            }
        }
        const el = document.getElementById(`info_group_${pk}`);
        if (el) {
            el.innerHTML = `${group.data.count} ta mijoz: $${thousand_separator(group.data.summa / 2)}`;
        }
    }
}

/* ─── Yangi lead DOM elementi ─── */
function newLeadobject(pk, name, date, summa, company, phone, created_user, validation, validation_date, service_type_name, district_name, business_type, investment_price, investment_valuta_display, referral_name) {
    let div = document.createElement("div");

    let nameHTML = validation
        ? `<div class="lead_name text-super">${ignore_null(name)}</div>`
        : `<div class="lead_name text-super" style="color:red!important;">${ignore_null(name)}</div>`;

    // Faqat to'ldirilgan fieldlarni ko'rsatish
    let fieldsHTML = '';

    if (validation_date) {
        fieldsHTML += `<div class="lead_timer" data-validity="${validation_date}T00:00:00" id="timer_${pk}"></div>`;
    }
    if (service_type_name) {
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Xizmat: <strong>${service_type_name}</strong></a></div>`;
    }
    if (phone) {
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Tel: <strong>${phone}</strong></a></div>`;
    }
    if (company) {
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Tashkilot: <strong>${company}</strong></a></div>`;
    }
    if (district_name) {
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Hudud: <strong>${district_name}</strong></a></div>`;
    }
    if (business_type) {
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Biznes: <strong>${business_type}</strong></a></div>`;
    }
    if (investment_price) {
        let valuta = investment_valuta_display ? ` <span style="color:#63b3ed;">(${investment_valuta_display})</span>` : '';
        fieldsHTML += `<div><a class="lead_other_price text-super d-block">Investitsiya: <strong>${thousand_separator(investment_price)}</strong>${valuta}</a></div>`;
    }

    let bottomRight = '';
    if (is_B2B()) {
        bottomRight = referral_name ? `<div class="lead_note text-super">${referral_name}</div>` : '';
    } else {
        bottomRight = `<div><a href="/edit/?id=${pk}"><i class="fa fa-info-circle" style="color:#6b778d;"></i></a></div>`;
    }

    div.innerHTML = `
        <div class="lead_card-header">
            ${nameHTML}
            <div class="lead_datediv text-super">
                <div class="lead_date">${date}</div>
                <div class="created">${created_user}</div>
            </div>
        </div>
        <div class="other_lead" style="margin-top:4px;">
            ${fieldsHTML}
        </div>
        <div class="lead_card-body" style="margin-top:6px;">
            <a class="lead_price text-super">${thousand_separator(summa)}</a>
            ${bottomRight}
        </div>`;

    div.setAttribute('pk', pk);
    div.draggable = true;
    div.classList.add('lead_card');
    div.id = `lead_${pk}`;
    addDragStartEvent(div);
    addDragEndEvent(div);
    return div;
}

/* ─── Footer drag events ─── */
function footerEnterDrag(e) {
    e.preventDefault();
    droppedElement = this;
    this.style.boxShadow  = '5px 10px 10px #888888';
    this.style.borderRadius = '5px';
}
function footerLeaveDrag() {
    this.style.boxShadow  = null;
    this.style.borderRadius = null;
}

function getBeforeGroup(pk) {
    let result, before_group;
    for (let group of Groups) {
        result = group.data.elements.find(o => o && o.id === pk);
        before_group = group;
        if (result !== undefined) break;
    }
    return before_group;
}

function getGroupNumberById(id) {
    for (const column of board_columns) {
        if (`group_body_${column.id}` === id) return column.id;
    }
}

/* ─── Drag-drop connections ─── */
function group_body_connections() {
    lead_card.forEach(item => { addDragStartEvent(item); addDragEndEvent(item); });

    group_body.forEach(list => {
        list.addEventListener('dragover',  e => e.preventDefault());
        list.addEventListener('dragenter', function (e) {
            e.preventDefault();
            droppedElement = this;
            this.style.backgroundColor = 'rgba(0,0,0,0.2)';
        });
        list.addEventListener('dragleave', function () {
            this.style.backgroundColor = defaultBgColor;
        });
        list.addEventListener('drop', function () {
            let pk           = parseInt(draggedItem.getAttribute('pk'));
            let before_group = getBeforeGroup(pk);
            if (this.id !== before_group.dom.id) {
                noted_handler.new_column_pk = getGroupNumberById(this.id);
                noted_handler.lead          = before_group.data.elements.find(o => o && o.id === pk);
                $('#lead_note_form')[0].reset();
                $('#lead_note_modal').modal('show');
            } else {
                droppedElement.style.backgroundColor = defaultBgColor;
            }
        });
    });
}

function updateLead(pk, name, price, company, address, phone, service_type_name, district_name, business_type, investment_price, investment_valuta_display, referral_name) {
    let index = leads_all.findIndex(i => i.id === pk);
    const obj = {
        id: pk, name, price,
        company:                   company                  || '',
        address:                   address                  || '',
        phone:                     phone                    || '',
        service_type_name:         service_type_name        || '',
        district_name:             district_name            || '',
        business_type:             business_type            || '',
        investment_price:          investment_price         || 0,
        investment_valuta_display: investment_valuta_display || '',
        referral_name:             referral_name            || '',
    };
    if (index !== -1) { leads_all[index] = { ...leads_all[index], ...obj }; }
    else              { leads_all.push(obj); }
}

function removeLead(pk) {
    let before_group     = getBeforeGroup(pk);
    let lead_object      = before_group.data.elements.find(o => o && o.id === pk);
    let lead_object_index = before_group.data.elements.findIndex(i => i && i.id === pk);
    if (lead_object) {
        before_group.data.summa -= lead_object.price;
        before_group.data.count -= 1;
    }
    before_group.data.elements.splice(lead_object_index, 1);
    const el = document.getElementById(`lead_${pk}`);
    if (el) el.remove();
}

function footer_buttons_connections() {
    const lead_loser = document.getElementById('lead_losed_footer');
    const lead_woned = document.getElementById('lead_woned_footer');

    [lead_loser, lead_woned].forEach(el => {
        el.addEventListener('dragover',  e => e.preventDefault());
        el.addEventListener('dragenter', footerEnterDrag);
        el.addEventListener('dragleave', footerLeaveDrag);
    });

    lead_loser.addEventListener('drop', function () {
        let pk           = parseInt(draggedItem.getAttribute('pk'));
        let before_group = getBeforeGroup(pk);
        losedLead = before_group.data.elements.find(o => o && o.id === pk);
        $('#lead_lose_form')[0].reset();
        $('#lead_lose_modal').modal('show');
        this.style.boxShadow = null; this.style.borderRadius = null;
    });

    lead_woned.addEventListener('drop', function () {
        let pk           = parseInt(draggedItem.getAttribute('pk'));
        let before_group = getBeforeGroup(pk);
        finishedLead = before_group.data.elements.find(o => o && o.id === pk);
        $('#lead_finished_form')[0].reset();
        $('#lead_finished_modal').modal('show');
        this.style.boxShadow = null; this.style.borderRadius = null;
    });
}

function getFormData(arr) {
    let obj = {};
    $.map(arr, n => { obj[n.name] = n.value; });
    return obj;
}

function addLeadToGroupAndUpdateLabels(response) {
    for (let i = 0; i < Groups.length; i++) {
        if (Groups[i].dom && Groups[i].dom.id === `group_body_${response.pole}`) {
            const obj = newLeadobject(
                response.id,
                response.name,
                response.date,
                response.price,
                response.company                   || '',
                response.phone                     || '',
                response.created_user              ? response.created_user.username : '',
                response.get_validity_period,
                response.validity_period           || '',
                response.service_type_name         || '',
                response.district_name             || '',
                response.business_type             || '',
                response.investment_price          || 0,
                response.investment_valuta_display || '',
                response.referral_name             || ''
            );
            updateLead(
                response.id,
                response.name,
                response.price,
                response.company,
                response.district,
                response.phone,
                response.service_type_name         || '',
                response.district_name             || '',
                response.business_type             || '',
                response.investment_price          || 0,
                response.investment_valuta_display || '',
                response.referral_name             || ''
            );
            Groups[i].dom.append(obj);
            Groups[i].data.count  += 1;
            Groups[i].data.summa  += response.price;
            Groups[i].data.elements.push(response);

            if (response.validity_period) {
                const timerEl = document.getElementById(`timer_${response.id}`);
                if (timerEl) startSingleCountdown(timerEl);
            }
            break;
        }
    }
    update_info_labels();
}

/* ════════════════════════════════════════
   DIRECTOR: POLE EDIT / DELETE
════════════════════════════════════════ */
$('.edit_pole_pen').on('click', function () {
    let pole_pk = parseInt(this.getAttribute("column_pk"));
    for (const boardColumn of board_columns) {
        if (pole_pk === boardColumn.id) {
            $('#edit_pole_form')[0].reset();
            $('#edit_pole_form input[name="name"]').val(boardColumn.name);
            $('#edit_pole_form input[name="number"]').val(boardColumn.number);
            $('#edit_pole_form input[name="id"]').val(boardColumn.id);
            $('#edit_pole').modal('show');
            break;
        }
    }
});

$('.delete_pole_pen').on('click', function () {
    let pole_pk = parseInt(this.getAttribute("column_pk"));
    for (const boardColumn of board_columns) {
        if (pole_pk === boardColumn.id) {
            swal({ title: `${boardColumn.name} maydonini o'chirmoqchimisiz?`, icon: "warning", buttons: ["Yo'q", "Ha"] })
                .then(willDelete => {
                    if (!willDelete) return;
                    $.ajax({
                        type: "GET", url: check_can_delete + '?pole_id=' + pole_pk,
                        beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
                        success: response => {
                            if (response.status === 500) {
                                let text = response.data.map(i => `${i['created_user__username']} da ${i['count']} ta\n`).join('');
                                swal(`Bu maydonni o'chirib bo'lmaydi.\n${text}`, { icon: "error" });
                            } else if (response.status === 200) {
                                $.ajax({
                                    type: "POST", url: delete_pole,
                                    beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
                                    data: { pole_id: pole_pk },
                                    success: () => location.reload()
                                });
                            }
                        }
                    });
                });
            break;
        }
    }
});

/* ════════════════════════════════════════
   DOCUMENT READY
════════════════════════════════════════ */
$(document).ready(function () {
    define_column_groups();
    define_groups_leads();
    group_body_connections();
    footer_buttons_connections();

    $('#phone_tel').mask('(000) 00 000 00 00');
    $('#phone_tel_edit').mask('(000) 00 000 00 00');

    /* ── Yangi lead button ── */
    $('#new_lead_button').on('click', function () {
        $('#newLeadForm')[0].reset();
        document.getElementById('phone_duplicate_info').style.display = 'none';
        $('#new_lead_modal').modal('show');
    });

    // Modal ochilganda toggle holatini qayta qo'llash
    $('#new_lead_modal').on('shown.bs.modal', function () {
        const STORE_KEY  = 'board_show_extra_fields';
        const saved      = localStorage.getItem(STORE_KEY);
        const isOpen     = saved === null ? true : saved === 'true';
        const toggle     = document.getElementById('toggle_extra_fields');
        const switchWrap = document.getElementById('toggle_switch_wrap');
        const extra      = document.getElementById('extra_fields_new');
        if (!toggle) return;
        toggle.checked = isOpen;
        if (isOpen) {
            switchWrap && switchWrap.classList.add('is-on');
            extra && extra.classList.remove('hidden');
            extra && extra.classList.add('visible');
        } else {
            switchWrap && switchWrap.classList.remove('is-on');
            extra && extra.classList.add('hidden');
            extra && extra.classList.remove('visible');
        }
        $("#new_lead_modal input").first().focus();
    });

    /* ── Yangi bosqich ── */
    $('#add_pole_btn').on('click', function () {
        $('#add_pole_form')[0].reset();
        $('#add_pole').modal('show');
    });

    /* ── Excel import ── */
    $('#import_excel').on('click', function () {
        $('#excelExportForm')[0].reset();
        new bootstrap.Modal(document.getElementById('ExcelExportModal')).show();
    });

    /* ── Modal focus ── */
    $("#edit_pole").on('shown.bs.modal', () => $("#edit_pole input").first().focus().select());
    $("#add_pole").on('shown.bs.modal', () => $("#add_pole input").first().focus());

    /* ── Yangi lead submit ── */
    $('#newLeadForm').submit(function (event) {
        event.preventDefault();
        let data     = getFormData($(this).serializeArray());
        let dataBody = {};

        if (is_B2B()) {
            dataBody = {
                name:            data['ism'],
                price:           parseInt(data['price']) || 0,
                company:         data['campany'],
                address:         data['district'],
                validity_period: data['validity_period'],
                phone:           get_telefon(data['phone']),
                referral:        data['referral'],
                service_type:    data['service_type'],
                user:            currentUser
            };
        } else {
            dataBody = {
                name:            data['ism'],
                validity_period: data['validity_period'],
                price:           parseInt(data['price']) || 0,
                phone:           get_telefon(data['phone']),
                referral:        data['referral'],
                service_type:    data['service_type'],
                user:            currentUser
            };
        }

        $.ajax({
            type: "POST", url: 'create_lead/',
            beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
            data: dataBody,
            success: function (response) {
                // Agar mavjud lead yangilangan bo'lsa — avval eski kartani olib tashlaymiz
                const existingEl = document.getElementById(`lead_${response.id}`);
                if (existingEl) {
                    removeLead(response.id);
                }
                addLeadToGroupAndUpdateLabels(response);
                $('#new_lead_modal').modal('hide');
            },
            error: err => console.log(err)
        });
    });

    /* ── Lead note (status o'zgartirish) ── */
    $("#lead_note_modal").on('shown.bs.modal', function () {
        $("#lead_note_modal textarea").first().focus();
        if (noted_handler.lead) $("#lead_note_form h5").first().html(noted_handler.lead.name);
    });
    $('#lead_note_modal').on('hidden.bs.modal', function () {
        if (droppedElement) droppedElement.style.backgroundColor = defaultBgColor;
    });
    $('#lead_note_form').submit(function (event) {
        event.preventDefault();
        let data      = getFormData($(this).serializeArray());
        let leadId    = noted_handler.lead.id;
        let newStatus = noted_handler.new_column_pk;

        // Mavjud lead ma'lumotlarini saqlab olamiz (district_name, service_type_name va h.k.)
        let existingLead = leads_all.find(o => o && o.id === leadId) || {};

        removeLead(leadId);
        $.ajax({
            type: "POST", url: 'change_lead_status/',
            beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
            data: { izoh: data['izoh'], lead: leadId, status: newStatus, user: currentUser },
            success: function(response) {
                // Response da bo'lmagan fieldlarni mavjud lead dan olamiz
                const merged = Object.assign({}, existingLead, response);
                addLeadToGroupAndUpdateLabels(merged);
                $('#lead_note_modal').modal('hide');
            }
        });
    });

    /* ── Yakunlash ── */
    $("#lead_finished_modal").on('shown.bs.modal', function () {
        $("#lead_finished_modal input").first().focus();
        if (finishedLead) $("#lead_finished_modal h5").first().html(`Yakunlash. Narx ${finishedLead.price}`);
    });
    $('#lead_finished_form').submit(function (event) {
        event.preventDefault();
        let data = getFormData($(this).serializeArray());
        $.ajax({
            type: "POST", url: 'lead_finished/',
            beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
            data: { price: data['price'], lead: finishedLead.id, user: currentUser },
            success: function (response) {
                removeLead(response.id);
                update_info_labels();
                $('#lead_finished_modal').modal('hide');
                finishedLead = null;
            }
        });
    });

    /* ── Yo'qotish ── */
    $("#lead_lose_modal").on('shown.bs.modal', () => $("#lead_lose_modal textarea").first().focus());
    $('#lead_lose_form').submit(function (event) {
        event.preventDefault();
        let data = getFormData($(this).serializeArray());
        $.ajax({
            type: "POST", url: 'lead_losed/',
            beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
            data: { izoh: data['izoh'], lead: losedLead.id, user: currentUser },
            success: function (response) {
                removeLead(response.id);
                update_info_labels();
                $('#lead_lose_modal').modal('hide');
                losedLead = null;
            }
        });
    });

    /* ── Lead tahrirlash (click on name) ── */
    $(document).on('click', '.lead_name', function () {
        let pk = parseInt(this.closest(".lead_card").getAttribute('pk'));
        editingLead = leads_all.find(o => o && o.id === pk);
        if (!editingLead) return;
        $('#edit_lead_modal').modal('show');
        $('#edit_lead_modal input[name="form_name"]').val(editingLead.name);
        $('#edit_lead_modal input[name="form_price"]').val(editingLead.price);
        $('#edit_lead_modal input[name="form_campany"]').val(editingLead.company || '');
        $('#edit_lead_modal input[name="form_address"]').val(editingLead.address || '');
        $('#edit_lead_modal input[name="form_phone"]').val(editingLead.phone || '');
        // ServiceType
        if (editingLead.service_type_id) {
            $('#edit_lead_modal select[name="service_type"]').val(editingLead.service_type_id);
        }
        $('#phone_tel_edit').trigger('input');
    });

    $("#edit_lead_modal").on('shown.bs.modal', () => $("#edit_lead_modal input").first().focus().select());

    $('#edit_lead_form').submit(function (event) {
        event.preventDefault();
        let data     = getFormData($(this).serializeArray());
        let bodyData = {
            lead:         editingLead.id,
            name:         data['form_name'],
            price:        parseInt(data['form_price']) || 0,
            company:      data['form_campany'],
            address:      data['form_address'],
            phone:        data['form_phone'],
            service_type: data['service_type'],
            user:         currentUser
        };

        let existingLead = leads_all.find(o => o && o.id === editingLead.id) || {};

        $.ajax({
            type: "POST", url: 'edit_lead/',
            beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
            data: bodyData,
            success: function(response) {
                removeLead(response.id);
                const merged = Object.assign({}, existingLead, response);
                addLeadToGroupAndUpdateLabels(merged);
                $('#edit_lead_modal').modal('hide');
            }
        });
    });

    define_groups_leads();
});

/* ── Excel import ── */
$('#import_excel').on('click', function () {
    $('#excelExportForm')[0].reset();
    new bootstrap.Modal(document.getElementById('ExcelExportModal')).show();
});

$('#excelExportForm').submit(function (event) {
    event.preventDefault();
    let formData = new FormData();
    formData.append('excel_file', $('#excelFile')[0].files[0]);
    formData.append('csrfmiddlewaretoken', csrf_token);
    $.ajax({
        url: '/import_leads_from_excel/', type: 'POST',
        data: formData, processData: false, contentType: false,
        beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", csrf_token),
        success: function (response) {
            if (response.status === 'success') {
                response.data.forEach(lead => addLeadToGroupAndUpdateLabels(lead));
                $('#excelExportForm')[0].reset();
                const modal = bootstrap.Modal.getInstance(document.getElementById('ExcelExportModal'));
                if (modal) modal.hide();
            }
        },
        error: (xhr, s, err) => console.log(err)
    });
});
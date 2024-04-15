let elements = []

function check_input(input) {
    return input.files.length !== 0
}

let image = document.getElementById('image')
let display_image = document.getElementById('display_image')
let loadImg = document.getElementById('loadImg')
let removeImg = document.getElementById('removeImg')
let addField = document.getElementById('addField')

image.onchange = evt => {
    const [file] = image.files
    if (file) {
        display_image.src = URL.createObjectURL(file)
        display_image.style.display = 'block'
        removeImg.style.display = ''
    }
}

loadImg.onclick = evt => {
    image.click()
}

removeImg.onclick = evt => {
    image.files = new DataTransfer().files
    display_image.src = ''
    display_image.style.display = 'none'
    removeImg.style.display = 'none'

}
addField.onclick = evt => {
    create_element()
}

function formSumbit() {

    if (!check_input(image)) {
        alert("Rasmni tanlang!")
        return false;
    } else {
        return true;
    }
}

function create_element() {
    let row = document.createElement('div')
    row.classList.add('row')
    row.innerHTML = `
                    <div class="col-sm-9 m-1">
                        <input type="text" class="form-control" name="field" required>
                    </div>
                    <div class="col-sm-2 m-1">
                        <i class="fa fa-remove fa-2x" onclick="remove_fields(this)"></i>
                    </div>`
    let field_content = document.getElementById('field_content')
    field_content.appendChild(row)
}

function remove_fields(obj) {
    console.log(obj.closest(".row").remove())
}
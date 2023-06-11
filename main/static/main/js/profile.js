let changedInputs = false
function addChangedInput(){
    changedInputs = true;
}

function editInfo(item){
    let btn_text = item.children[0].innerHTML.split(" ")
    let inputs = document.getElementsByClassName("input")
    if (btn_text[0] == "Edit"){
        btn_text[0] = "Save"
        for (let i = 0 ; i < inputs.length; i++){
            inputs[i].disabled = false
        }
    } else {
        btn_text[0] = "Edit"
        if (changedInputs == true){
            document.getElementById("editInfoForm").submit()
        }
        else {
            for (let i = 0 ; i < inputs.length; i++){
                inputs[i].disabled = true
            }
        }
    } 
    item.children[0].innerHTML = btn_text.join(" ")
}

function imgUploadBtn(){
    document.getElementById("imgUploadInput").click();
    document.getElementById("imgUploadInput").onchange = function() {
        document.getElementById("imgUploadForm").submit();
    };
}

function editContactInfo(id, first_name, last_name, card_number, is_business){
    let el = document.getElementById("editContactModal")
    form = el.children[0].children[1].children[0]
    form.id = 'editContactForm' + id
    form.action = 'edit-contact/' + id + '/'

    delete_a_tag = el.children[0].children[2].children[1]
    delete_a_tag.href = 'delete-contact/' + id + '/'

    inputs = form.getElementsByClassName('input')

    inputs[0].value = first_name
    inputs[1].value = last_name
    inputs[2].value = card_number

    if (is_business == 'False'){
        inputs[3].checked = false
        inputs[3].value = false
    } else {
        inputs[3].checked = true
        inputs[3].value = true
    }
}

function submitEditContactForm(tag){
    is_business = tag.parentNode.parentNode.children[1].children[0].children[1].children[6].children[1]
    if(is_business.checked == true){
        is_business.value = 'on'
    } else {
        is_business.value = null
    }
    tag.parentNode.parentNode.children[1].children[0].submit()
}

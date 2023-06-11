let changedInputs = false
function addChangedInput(changedInput){
    changedInputs = true;
}

function messageEnable(tId){
    notes = document.getElementsByName('note')
    element = document.getElementById('note' + tId)
    for(i=0; i < notes.length; i++){
        if(notes[i] != element)
        notes[i].hidden = true
    }
    if(element.hidden == false){
        element.hidden = true
    } else {
        element.hidden = false
    }
}

function edit(tId){
    row = document.getElementById(tId)
    button = row.getElementsByClassName("edit_button")[0]
    inputs = row.getElementsByClassName("input")
    if(button.value == "Edit"){
        button.value = "Save"
        button.innerHTML = "Save"
        for(let i = 0; i < inputs.length; i++){
            inputs[i].disabled = false
        }
    } else {
        if (changedInputs == true ){
            row.getElementsByTagName("form")[0].submit()
        } else {
            button.value = "Edit"
            button.innerHTML = "Edit"
            for(let i = 0; i < inputs.length; i++){
                inputs[i].disabled = true
            }
        }
    }
}

function changeAction(tId){
    addChangedInput()
    action_button = document.getElementById(tId).getElementsByClassName('action_button')[0]
    action_input = action_button.getElementsByClassName('action_input')[0]
    if(action_input.value == 'deposit'){
        action_input.value = 'withdraw'
        action_button.getElementsByClassName('green_arrow')[0].style.opacity = '0.2'
        action_button.getElementsByClassName('red_arrow')[0].style.opacity = '1'
    } else if(action_input.value == 'withdraw'){
        action_input.value = 'deposit'
        action_button.getElementsByClassName('green_arrow')[0].style.opacity = '1'
        action_button.getElementsByClassName('red_arrow')[0].style.opacity = '0.2'
        
    }

}

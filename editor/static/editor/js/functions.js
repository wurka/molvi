function saveFileDialog_onkeydown(event) {
    console.log(event);
    /*if (event.keyCode === 13) {
        $('#saveFileDialog_okbutton').click()
    }*/
}

$(document).ready(()=> {
        let element = document.getElementById("saveFileDialog");
        element.addEventListener("keydown", (event)=>{
            console.log(event.code);
            if (event.code === "Enter") {
                $("#saveFileDialog_okbutton").click();
            }
        })
    }
);
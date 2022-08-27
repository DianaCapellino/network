document.addEventListener('DOMContentLoaded', function() {
    all_edit_buttons = document.querySelectorAll('.edit-buttons');
    all_textareas = document.querySelectorAll('.new-textareas');

    all_textareas.forEach((element) => {
        element.style.display ='none';
    });

    all_edit_buttons.forEach((post) => {
        post.addEventListener("click", () => {
            edit_post(post.id);
        });
    });

})

function edit_post(post_id) {

}
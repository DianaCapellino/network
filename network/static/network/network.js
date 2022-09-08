document.addEventListener('DOMContentLoaded', function() {

    // Get the elements buttons and textareas
    const all_edit_buttons = document.querySelectorAll('.edit-buttons');
    const all_save_buttons = document.querySelectorAll('.save-buttons');
    const all_textareas = document.querySelectorAll('.new-textareas');
    const all_like_buttons = document.querySelectorAll('.like-buttons');

    // Hide all the textareas
    all_textareas.forEach((element) => {
        element.style.display='none';
    });

    // Hide all the save buttons
    all_save_buttons.forEach((post) => {
        post.style.display='none';
    });

    // Send post id when it clicks
    all_edit_buttons.forEach((post) => {
        post.addEventListener("click", () => {
            edit_post(post.id);
        });
    });

    // For each like button that the user already like, change to Unlike
    fetch('/likes')
    .then(response => response.json())
    .then(like => {

        // Get all the like buttons
        all_like_buttons.forEach((button) => {

            // Add event listeners for each like button
            button.addEventListener("click", () => {
                like_post(button.id);
            });

            // Change to unlike just the ones in the list
            like.forEach((item) => {
                if (parseInt(button.id) === item.post_id) {
                    const btn = document.querySelector(`#like-btn-${button.id}`).firstElementChild
                    btn.innerHTML="UNLIKE";
                };
            })
        });
    });
});


// Function to edit the posts with post id
function edit_post(post_id) {

    // Get the element texarea and buttons of this specific post
    const textarea = document.querySelector(`#textarea-${post_id}`);
    const edit_content = document.querySelector(`#post-content-${post_id}`);
    const save_button = document.querySelector(`#save-button-${post_id}`);
    const edited_button = document.querySelector(`#edited-button-${post_id}`);

    // Hide the content of the post
    edit_content.style.display='none';
    
    // Get the current content of the post
    fetch(`/post/${post_id}`)
    .then(response => response.json())
    .then(post => {

        // Show the text area with current content of the post
        textarea.style.display='block';
        textarea.innerHTML=`${post.content}`;

        // Hide edit button and display save button with functionality to click
        edited_button.style.display='none';
        save_button.style.display='block';
        save_button.addEventListener("click", () => {
            save_post(post.id, textarea.value);
        });
    });
}


// To save changes of the edited posts
function save_post(post_id, new_content) {

    // Update content of the post
    fetch(`/post/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          content: `${new_content}`
        })
    });

    // Update content in HTML
    const new_post_content = document.querySelector(`#post-content-${post_id}`);
    new_post_content.innerHTML = new_content;

    // Hide textarea and save button and display edit button and content again
    document.querySelector(`#textarea-${post_id}`).style.display='none';
    document.querySelector(`#save-button-${post_id}`).style.display='none';
    document.querySelector(`#edited-button-${post_id}`).style.display='block';
    new_post_content.style.display='block';
}


function like_post (post_id) {

    // Update likes in the backend
    fetch(`/post/${post_id}/like`)
    .then(answer => {
        
        // Update the like button getting the info from the likes
        fetch('/likes')
        .then(response => response.json())
        .then(like => {

            like.forEach((item) => {
                if (parseInt(post_id) === item.post_id) {
                    const btn = document.querySelector(`#like-btn-${post_id}`).firstElementChild
                    btn.innerHTML="UNLIKE";
                }
                else {
                    const btn = document.querySelector(`#like-btn-${post_id}`).firstElementChild
                    btn.innerHTML="LIKE";
                }
            })
        });

        // Get the updated likes
        fetch(`/post/${post_id}`)
        .then(response => response.json())
        .then(post => {

            // Update likes in the post
            document.querySelector(`#like-${post_id}`).innerHTML=` ${post.likes}`;
        });
    });
}
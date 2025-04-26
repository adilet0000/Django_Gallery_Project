document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.querySelector('.comment-form');
    if (!commentForm) return;

    commentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        formData.append('comment_submit', 'true');

        fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentsList = document.querySelector('.comments-list');
                const newComment = document.createElement('div');
                newComment.className = 'comment-item';
                newComment.innerHTML = `
                    <strong class="comment-author">${data.comment.username}</strong>
                    <p class="comment-text">${data.comment.text}</p>
                    <small class="comment-date">${data.comment.created_at}</small>
                    ${data.comment.is_author ? `
                    <div class="comment-actions">
                        <a href="/comment/edit/${data.comment.id}/" class="btn btn-sm btn-warning">Редактировать</a>
                        <a href="/comment/delete/${data.comment.id}/" class="btn btn-sm btn-danger">Удалить</a>
                    </div>
                    ` : ''}
                `;
                
                if (commentsList.querySelector('.no-comments')) {
                    commentsList.innerHTML = '';
                }
                
                commentsList.insertBefore(newComment, commentsList.firstChild);
                this.reset();
            }
        });
    });
});



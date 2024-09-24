function vote(type, commentId) {
    fetch('/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: type, 
            id: commentId
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Atualiza os elementos na página com os novos valores de likes e dislikes
        document.getElementById(`likes-${commentId}`).innerText = data.likes;
        document.getElementById(`dislikes-${commentId}`).innerText = data.dislikes;
    })
    .catch(error => console.error('Erro:', error));
}

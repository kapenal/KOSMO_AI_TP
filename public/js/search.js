document.getElementById('search_btn').addEventListener('click', async function() {
    const searchText = document.getElementById("search_text").value;

    try {
        // 서버로 POST 요청 보내기
        const response = await fetch('/search_movie', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: searchText })
        });

        // 서버로부터 받은 응답에서 searchURL을 확인
        const data = await response.json();
        console.log("search.js : ", data.movies)
        if (data.movies) {
            localStorage.setItem('searchData', JSON.stringify({
                input_title: searchText,
                searchResult: data.movies
                
        }))};
        
        window.location.href = `/html/search_list.html`;
        
    } catch (error) {
        console.error('서버 오류:', error);
    }
});
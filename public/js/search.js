// 검색 기능 함수
async function executeSearch(searchText) {
    try {
        const response = await fetch('/search_movie', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: searchText })
        });

        const data = await response.json();
        console.log("search.js : ", data.movies);
        if (data.movies) {
            localStorage.setItem('searchData', JSON.stringify({
                input_title: searchText,
                searchResult: data.movies
            }));
        }
        window.location.href = `/html/search_list.html`;

    } catch (error) {
        console.error('서버 오류:', error);
    }
}

// 검색 버튼 클릭 이벤트
document.getElementById('search_btn').addEventListener('click', function() {
    const searchText = document.getElementById("search_text").value;
    executeSearch(searchText);
});
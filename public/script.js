// script.js
// index.html에서 검색버튼 클릭 시 일어나는 이벤트
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
        console.log("encodeURI : ", data.movie)
        if (data.movie) {
        const movieString = JSON.stringify(data.movie);  // 객체 → 문자열
            // const encodedMovie = encodeURIComponent(movieString);  // 문자열 → URL 안전하게 인코딩
            // searchURL을 parameter로 붙여서 search.html로 이동
            // window.location.href = `search_list.html?search_movie=${encodeURIComponent(movieString)}`;
            window.location.href = `search_list.html?search_movie=${encodeURIComponent(movieString)}&keyword=${encodeURIComponent(searchText)}`;

        }
    } catch (error) {
        console.error('서버 오류:', error);
    }
    
});


// search_list.html에서 상세페이지(임시) 버튼 클릭 시 일어나는 이벤트
document.getElementById('search_btn').addEventListener('click', async function() {
    const searchText = document.getElementById("search_text").value;

    try {
        // detail_page.html로 이동
        // window.location.href = "detail_page.html";

        // 서버로 POST 요청 보내기
        // const response = await fetch('/do-something', {
        //     method: 'POST',
        //     headers: {'Content-Type': 'application/json'},
        //     body: JSON.stringify({ text: searchText })
        // });

        // // 서버로부터 받은 응답에서 search_url을 확인
        // const data = await response.json();
        // console.log("encodeURI : ", data.search_url)
        // if (data.search_url) {
        //     // search_url을 query parameter로 붙여서 search.html로 이동
        //     window.location.href = `search_list.html?search_url=${encodeURIComponent(data.search_url)}`;
        // }
    } catch (error) {
        console.error('서버 오류:', error);
    }
    
});
// script.js
document.getElementById('search_btn').addEventListener('click', async function() {
    const searchText = document.getElementById("search_text").value;

    try {
        // 서버로 POST 요청 보내기
        const response = await fetch('/do-something', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: searchText })
        });

        // 서버로부터 받은 응답에서 search_url을 확인
        const data = await response.json();
        console.log("encodeURI : ", data.search_url)
        if (data.search_url) {
            // search_url을 query parameter로 붙여서 search.html로 이동
            window.location.href = `search2.html?search_url=${encodeURIComponent(data.search_url)}`;
        }
    } catch (error) {
        console.error('서버 오류:', error);
    }
    
});
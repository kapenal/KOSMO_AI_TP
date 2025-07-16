// search_list.html에서 상세페이지(임시) 버튼 클릭 시 일어나는 이벤트
document.getElementById('detail_btn').addEventListener('click', async function() {
    const searchText = document.getElementById("search_text").value;

    try {
        // 서버로 POST 요청 보내기
        const response = await fetch('/do-recommend', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: searchText })
        });

        const data = await response.json();

        // 서버 응답을 정상적으로 받았을 경우에만 페이지 이동
        if (data && data.recommendations) {
            // data 전체를 localStorage에 저장하거나,
            // 필요한 데이터만 query string으로 넘길 수도 있음
            // console.log("추천 데이터:", data);
            // console.log("추천 데이터:", data.recommendations);
            localStorage.setItem('recommendData', JSON.stringify(data));
            
            // 페이지 이동
            window.location.href = 'detail_page.html';
        } else {
            console.error('추천 데이터 없음:', data);
        }
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
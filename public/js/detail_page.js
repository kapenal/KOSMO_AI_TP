

// // 상세 페이지 영화 정보 호출
// app.get('/movie/:id', async (req, res) => {
//     const movieId = req.params.id;

//     const movie = await getMovieFromPython(movieId);  // ✅ await OK

//     if (!movie) {
//     return res.status(404).send('영화를 찾을 수 없습니다.');
//     }

//     res.send(`
//         <h1>${movie.제목}</h1>
//         <img src="${movie.포스터}">
//         <p>⭐ 별점: ${movie.별점}</p>
//         <p>${movie.개요}</p>
//         <a href="/">← 목록으로</a>
//     `);
// });

// window.addEventListener('DOMContentLoaded', () => {
//     const movieId = getMovieIdFromURL();  // 예: URL에서 /movie/123 추출
//     console.log("영화 ID:", movieId);
//     fetch(`/api/movie/${movieId}`)
//         .then(res => res.json())
//         .then(movie => {
//             const movieDiv = document.getElementById('movie-detail');
//             movieDiv.innerHTML = `
//                 <img src="${movie.poster_path}" style="width: 200px; height: 300px;" alt="${movie.title_ko}">
//                 <p><strong>제목:</strong> ${movie.title_ko}</p>
//                 <p><strong>장르:</strong> ${(movie.genres || []).join(', ')}</p>
//                 <p><strong>개봉일:</strong> ${movie.release_date}</p>
//                 <p><strong>평점:</strong> ${movie.vote_average.toFixed(1)}</p>
//             `;
//         })
//         .catch(err => {
//             console.error('영화 정보 불러오기 실패:', err);
//         });
// });

// function getMovieIdFromURL() {
//     const parts = window.location.pathname.split('/');
//     return parts[parts.length - 1]; // /movie/123 → '123'
// }

window.addEventListener('DOMContentLoaded', () => {
      const parts = window.location.pathname.split('/');
      const movieId = parts[parts.length - 1];

      fetch(`/api/movie/${movieId}`)
        .then(res => res.json())
        .then(movie => {
          const movieDiv = document.getElementById('movie-detail');
          movieDiv.innerHTML = `
            <h1>${movie.제목}</h1>
            <p>장르: ${movie.장르.join(', ')}</p>
            <p>연도: ${movie.연도}</p>
            <p>평점: ${movie.평점}</p>
        `;
        })
        .catch(err => {
          console.error('영화 상세 불러오기 실패:', err);
          document.getElementById('movie-detail').textContent = '영화 정보를 불러올 수 없습니다.';
        });
    });
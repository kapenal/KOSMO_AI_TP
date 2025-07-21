// // 영화 상세 페이지
// window.addEventListener('DOMContentLoaded', () => {
//   const parts = window.location.pathname.split('/');
//   const movieId = parts[parts.length - 1];
//   const params = new URLSearchParams(window.location.search);
//   const title = params.get('title') || '';
//   loadRecommendations(title);  // 추천 영화
  
//   fetch(`/api/movie/${movieId}`)
//     .then(res => res.json())
//     .then(movie => {
//       // 영화 정보 삽입
//       document.getElementById('title_ko').textContent = `${movie.제목}`;
//       // document.getElementById('title_en').textContent = movie.영문제목 || '';
//       document.getElementById('release_date').textContent = `${movie.연도}`;
//       // document.getElementById('runtime').textContent = `상영시간: ${movie.상영시간 || '-'}분`;
//       document.getElementById('rating_value').textContent = `${movie.평점}`;
//       // document.getElementById('director').textContent = movie.감독 || '-';
//       // document.getElementById('actors').textContent = (movie.출연진 || []).join(', ');
//       document.getElementById('overview').textContent = movie.줄거리 || '줄거리 정보가 없습니다.';
//       document.getElementById('genres').textContent = movie.장르.join(', ');
//       // // 장르 뱃지
//       // const genreContainer = document.getElementById('genre_badges');
//       // genreContainer.innerHTML = '';
//       // (movie.장르 || []).forEach(genre => {
//       //   const span = document.createElement('span'); 
//       //   span.className = 'badge bg-secondary me-1';
//       //   span.textContent = genre;
//       //   genreContainer.appendChild(span);
//       // });

//       // 포스터 이미지
//       if (movie.포스터) {
//         const posterImg = document.getElementById('poster');
//         posterImg.src = movie.포스터;
//         posterImg.classList.remove('d-none');
//         document.getElementById('poster_empty').classList.add('d-none');
//       }
//     })
//     .catch(err => {
//       console.error('영화 상세 불러오기 실패:', err);
//       document.getElementById('overview').textContent = '영화 정보를 불러올 수 없습니다.';
//     });
// });

window.addEventListener('DOMContentLoaded', () => {
  const parts = window.location.pathname.split('/');
  const movieId = parts[parts.length - 1];
  const params = new URLSearchParams(window.location.search);
  const title = params.get('title') || '';
  loadRecommendations(title);  // 추천 영화
  loadMovieDetail(movieId);   // 영화 상세 정보
  loadReviews(movieId);       // 리뷰 출력
});

// 영화 상세 데이터
function loadMovieDetail(movieId) {
  fetch(`/api/movie/${movieId}`)
    .then(res => res.json())
    .then(movie => {
      document.getElementById('title_ko').textContent = `${movie.제목}`;
      document.getElementById('release_date').textContent = `${movie.연도}`;
      document.getElementById('rating_value').textContent = `${movie.평점}`;
      document.getElementById('overview').textContent = movie.줄거리 || '줄거리 정보가 없습니다.';
      document.getElementById('genres').textContent = movie.장르.join(', ');

      if (movie.포스터) {
        const posterImg = document.getElementById('poster');
        posterImg.src = movie.포스터;
        posterImg.classList.remove('d-none');
        document.getElementById('poster_empty').classList.add('d-none');
      }
    })
    .catch(err => {
      console.error('영화 상세 불러오기 실패:', err);
      document.getElementById('overview').textContent = '영화 정보를 불러올 수 없습니다.';
    });
}



// 추천 영화 데이터 리스트
// window.onload = function () {
//   const params = new URLSearchParams(window.location.search);
//   const titleFromUrl = params.get('title') || '';
//   console.log("추천 영화 제목:", titleFromUrl);
//   if (titleFromUrl) {
//     fetch(`/api/recommend?title=${encodeURIComponent(titleFromUrl)}`)
//       .then(res => res.json())
//       .then(recommendData => {
//         console.log("추천 데이터:", recommendData);

//         // document.getElementById('search_text').value = recommendData.input_title || '';
//         const container = document.getElementById('recommend_list');

//         container.innerHTML = ''; // 기존 추천 영화 지우기

//       recommendData.recommendations.forEach((movie, index) => {
//         const movieDiv = document.createElement('div'); // ✅ 반복 안에서 새로 생성
//         movieDiv.className = 'recommend-item bg-secondary';
//         movieDiv.style.cssText = "width: 220px; height: 350px; text-align: center; padding: 10px; box-sizing: border-box;";

//         movieDiv.innerHTML = `
//             <a href="/movie/${movie.link}?title=${encodeURIComponent(movie.title_ko)}" style="text-decoration: none; color: inherit;">
//               <img src="${movie.poster_path}" style="width: 150px; height: 250px;" alt="${movie.title_ko}">
//               <p align="center"><strong>제목:</strong> ${movie.title_ko}</p>
//               <p align="center"><strong>장르:</strong> ${(movie.genres || []).slice(0, 2).join(', ')}</p>
//             </a>
//         `;

//         container.appendChild(movieDiv);
//       });
//       })
//       .catch(err => {
//         console.error("추천 영화 불러오기 실패:", err);
//       });
//   } else {
//     console.error("추천 데이터가 없습니다.");
//   }
// };

// function loadReviews(movieId) {
//   fetch(`/api/reviews/${movieId}`)
//     .then(res => res.json())
//     .then(data => {
//       const reviewContainer = document.getElementById('review_list');
//       reviewContainer.innerHTML = ''; // 기존 리뷰 지우기

//       data.reviews.forEach(review => {
//         const div = document.createElement('div');
//         div.className = 'review-item';
//         div.innerHTML = `
//           <p><strong>${review.name}</strong></p>
//           <p>${review.content}</p>
//           <p>❤️ ${review.like}</p>
//         `;
//         reviewContainer.appendChild(div);
//       });
//     })
//     .catch(err => {
//       console.error('리뷰 불러오기 실패:', err);
//     });
// }

function loadRecommendations(title) {
  fetch(`/api/recommend?title=${encodeURIComponent(title)}`)
    .then(res => res.json())
    .then(recommendData => {
      const container = document.getElementById('recommend_list');
      container.innerHTML = '';

      recommendData.recommendations.forEach(movie => {
        const movieDiv = document.createElement('div');
        movieDiv.className = 'recommend-item bg-secondary';
        movieDiv.style.cssText = "width: 220px; height: 350px; text-align: center; padding: 10px; box-sizing: border-box;";

        movieDiv.innerHTML = `
          <a href="/movie/${movie.link}?title=${encodeURIComponent(movie.title_ko)}" style="text-decoration: none; color: inherit;">
            <img src="${movie.poster_path}" style="width: 150px; height: 250px;" alt="${movie.title_ko}">
            <p><strong>제목:</strong> ${movie.title_ko}</p>
            <p><strong>장르:</strong> ${(movie.genres || []).slice(0, 2).join(', ')}</p>
          </a>
        `;

        container.appendChild(movieDiv);
      });
    })
    .catch(err => {
      console.error("추천 영화 불러오기 실패:", err);
    });
}

// 리뷰 데이터
function loadReviews(movieId) {
  fetch(`/api/review/${movieId}`)
    .then(res => res.json())
    .then(data => {
      const reviewContainer = document.getElementById('review_list');
      reviewContainer.innerHTML = ''; // 기존 리뷰 지우기

      // data 자체가 배열이므로 data.forEach 사용
      data.forEach(review => {
        const div = document.createElement('div');
        div.className = 'review-item';
        div.innerHTML = `
          <p><strong>${review.닉네임}</strong></p>
          <p>${review.리뷰}</p>
          <p>평점: ${review.평점}</p>
        `;
        reviewContainer.appendChild(div);
      });
    })
    .catch(err => {
      console.error('리뷰 불러오기 실패:', err);
    });
}
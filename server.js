// server.js
const express = require('express');
const app = express();
const port = 3000;
const { spawn } = require('child_process');
const path = require("path");
const { urlencoded } = require('body-parser');

// 추가한 바디 파싱
app.use(express.urlencoded({ extended: true }));

// JSON 파싱 미들웨어 추가
app.use(express.json());

// 정적 파일 제공 (HTML, JS 파일을 제공)
app.use(express.static('public')); // index.html과 script.js를 제공

// 기본 라우트 처리 - index.html로 연결
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'html', 'index.html'));
});

// POST 요청 처리
// app.post('/search_movie', (req, res) => {
//     const searchText = req.body.text;  // 클라이언트에서 보낸 'text' 값
//     console.log(searchText + ' 버튼이 클릭되었어요!');

//     // Python 스크립트 실행
//     const pythonProcess = spawn(
//         'python',
//         // [path.join(__dirname, "public",  "py", "search_movies.py"), searchText]
//         [path.join(__dirname, "public",  "py", "search_movies.py"), searchText]
//     );
    
//     // Python 프로세스 실행 후 결과 처리
//     pythonProcess.stdout.on('data', (data) => {
//         try {
//             const output = JSON.parse(data.toString()); // 반환된 main.py의 search_url이 data 매개변수로 받아옴
//             console.log("movie_title", output)
//             // searchURL을 클라이언트(script.js) 반환
//             res.json({ movie : output });
//         } catch (error) {
//             console.error('JSON 파싱 오류:', error);
//             res.status(500).json({ error: 'Python 결과 처리 중 오류 발생' });
//         }
//     });

//     pythonProcess.stderr.on('data', (data) => {
//         console.error(`Python Error: ${data.toString()}`);
//         res.status(500).json({ error: 'Python 스크립트 실행 중 오류 발생' });
//     });

//     pythonProcess.on('close', (code) => {
//         console.log(`Python process exited with code ${code}`);
//     });
// });


// POST 요청 처리
app.post('/search_movie', (req, res) => {
    const searchText = req.body.text;  // 클라이언트에서 보낸 'text' 값
    console.log(searchText + ' 버튼이 클릭되었어요!');

    // Python 스크립트 실행
    const pythonProcess = spawn(
        'python',
        // [path.join(__dirname, "public",  "py", "search_movies.py"), searchText]
        [path.join(__dirname, "public",  "py", "search_movies_list.py"), searchText]
    );
    
    // Python 프로세스 실행 후 결과 처리
    pythonProcess.stdout.on('data', (data) => {
        try {
            const output = JSON.parse(data.toString()); // 반환된 main.py의 search_url이 data 매개변수로 받아옴
            // console.log("movie_title", output)
            // searchURL을 클라이언트(script.js) 반환
            res.json({ movies : output });
        } catch (error) {
            console.error('JSON 파싱 오류:', error);
            res.status(500).json({ error: 'Python 결과 처리 중 오류 발생' });
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data.toString()}`);
        res.status(500).json({ error: 'Python 스크립트 실행 중 오류 발생' });
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
});


// POST 요청 처리 - 영화 추천
app.post('/do-recommend', (req, res) => {
    const searchText = req.body.text;
    console.log(searchText + ' detail page에서 버튼이 클릭되었어요!');

    const pythonProcess = spawn(
        "python",
        [path.join(__dirname, "public",  "py", "recommend.py"), searchText]
    );

    let dataBuffer = "";
    let errorBuffer = "";

    pythonProcess.stdout.on('data', (chunk) => {
        dataBuffer += chunk.toString('utf8');
    });

    pythonProcess.stderr.on('data', (chunk) => {
        errorBuffer += chunk.toString('utf8');
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python 프로세스 오류 종료 코드: ${code}`);
            console.error(`stderr: ${errorBuffer}`);
            return res.status(500).json({ error: 'Python 스크립트 실행 실패' });
        }
        try {
            const output = JSON.parse(dataBuffer);
            console.log("Python에서 받은 추천 데이터:", output);
            res.json({
                input_title: output.input_title,
                recommendations: output.recommendations
            });
        } catch (error) {
            console.error('JSON 파싱 오류:', error);
            console.error('수신 데이터:', dataBuffer);
            res.status(500).json({ error: 'Python 결과 처리 중 오류 발생' });
        }
    });
});

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
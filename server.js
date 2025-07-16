// server.js
const express = require('express');
const app = express();
const port = 3000;
const { spawn } = require('child_process');
const path = require("path");

// JSON 파싱 미들웨어 추가
app.use(express.json());

// 정적 파일 제공 (HTML, JS 파일을 제공)
app.use(express.static('public')); // index.html과 script.js를 제공

// POST 요청 처리
app.post('/do-something', (req, res) => {
    const searchText = req.body.text;  // 클라이언트에서 보낸 'text' 값
    console.log(searchText + ' 버튼이 클릭되었어요!');

    // Python 스크립트 실행
    const pythonProcess = spawn(
        "C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
        [path.join(__dirname, "public", "main.py"), searchText]
    );
    
    // Python 프로세스 실행 후 결과 처리
    pythonProcess.stdout.on('data', (data) => {
        try {
            const output = JSON.parse(data.toString()); // 반환된 main.py의 search_url이 data 매개변수로 받아옴
            const searchURL = output.search_url;  // search_url의 값만 따로 searchURL에 넣어줌

            // searchURL을 클라이언트(script.js) 반환
            res.json({ search_url: searchURL });
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

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port} 에서 실행 중입니다.`);
});
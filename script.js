document.addEventListener("DOMContentLoaded", function () {
    fetch('http://127.0.0.1:5000/get_course_data') // ✅ 確保 Flask API 正常運行
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ 成功獲取課程資料:", data); // 🔍 Debug，檢查 JSON 是否正確

            // ✅ 確保 API 有返回資料
            if (!data || data.error) {
                console.error("❌ 錯誤: API 返回錯誤", data.error || "無法獲取資料");
                return;
            }

            // ✅ 顯示課程資訊
            document.getElementById("teacher").textContent = data.teacher || "N/A";
            document.getElementById("course_name").textContent = data.course_name || "N/A";
            document.getElementById("description").textContent = data.description || "N/A";
            document.getElementById("class").textContent = data.class || "N/A";
            document.getElementById("grading").textContent = data.grading || "N/A";
            document.getElementById("credits").textContent = data.credits || "N/A";
            document.getElementById("hours").textContent = data.hours || "N/A";
            document.getElementById("schedule").textContent = data.schedule || "N/A";
            document.getElementById("location").textContent = data.location || "N/A";

            // ✅ 顯示學生列表
            let studentList = document.getElementById("student-list");
            studentList.innerHTML = ""; // 清空舊的內容

            if (Array.isArray(data.students) && data.students.length > 0) {
                data.students.forEach(student => {
                    let row = `<tr>
                        <td>${student.account}</td>
                        <td>${student.name}</td> 
                        <td>${student.gender}</td>
                    </tr>`;
                    studentList.innerHTML += row;
                });
            } else {
                studentList.innerHTML = "<tr><td colspan='3'>❌ 無學生資料</td></tr>";
            }
        })
        .catch(error => console.error("❌ 錯誤: 無法加載課程資料", error));
});









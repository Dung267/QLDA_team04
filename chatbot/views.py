# chatbot/views.py
from django.shortcuts import render, redirect

def _get_bot_answer(question: str) -> str:
    q = question.lower()

    if "ngập" in q:
        return "Bạn nên tránh các tuyến đường trũng thấp và theo dõi mục Alerts."
    if "đăng nhập" in q:
        return "Bạn vào menu Accounts để đăng nhập hoặc đăng ký tài khoản."
    if "phản ánh" in q:
        return "Bạn vào mục Incidents > Report để gửi phản ánh sự cố."
    if "bảo trì" in q:
        return "Bạn vào mục Maintenance để tạo và theo dõi yêu cầu bảo trì."
    return "Mình đã ghi nhận câu hỏi. Phiên bản chatbot demo hiện đang trả lời theo từ khóa."

def ask_chatbot(request):
    history = request.session.get("chat_history_demo", [])

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if question:
            answer = _get_bot_answer(question)
            history.append({"question": question, "answer": answer})
            request.session["chat_history_demo"] = history
            request.session.modified = True
            return redirect("/chatbot/history/")

    return render(request, "chatbot/ask.html")


def chat_history(request):
    history = request.session.get("chat_history_demo", [])
    return render(request, "chatbot/history.html", {"history": history})
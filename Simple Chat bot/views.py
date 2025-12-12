from django.shortcuts import render
from .rag import SimpleRAG, youtube_recommendation
rag = SimpleRAG()

def home(request):
    answer = ""
    status = ""
    error = ""

    # initialize chat history if not exists
    if "history" not in request.session:
        request.session["history"] = []

    if request.method == "POST":

        # Upload PDF
        if "pdf" in request.FILES:
            file = request.FILES["pdf"]
            try:
                rag.add_pdf(file, file.name)
                status = f"Uploaded: {file.name}"
            except Exception as e:
                error = f"Error uploading PDF: {e}"

        # Ask question
        else:
            question = request.POST.get("question", "")
            try:
                answer = rag.answer(question)
                yt_link = youtube_recommendation(question)

                # store in history
                history = request.session.get("history", [])
                history.append({
                    "question": question,
                    "answer": answer,
                    "youtube": yt_link,
                })
                request.session["history"] = history
                request.session.modified = True

            except Exception as e:
                error = f"Error answering: {e}"

    context = {
        "answer": answer,
        "status": status,
        "error": error,
        "pdfs": rag.pdf_names,
        "history": request.session["history"],  # <<<< send history to HTML
        "yt_link": yt_link if 'yt_link' in locals() else "",

    }
    return render(request, "chat.html", context)

def prepare_data():

    # Build the RAG
    with open("./knowledge/JS6.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print(content)

prepare_data()
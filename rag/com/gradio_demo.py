import gradio as gr
from rag.com.utils_ref import search, generate_answer

def search_interface(query: str, include_sentiment: bool = False, filename: str = None):
    results = search(query, include_sentiment=include_sentiment, filename=filename)
    return str(results)

def generate_interface(query: str):
    return generate_answer(query)

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# RAG System Demo")
    
    with gr.Tab("Search"):
        with gr.Row():
            query_input = gr.Textbox(label="Search Query")
            sentiment_checkbox = gr.Checkbox(label="Include Sentiment Analysis")
            filename_input = gr.Textbox(label="Filename (optional)")
        search_button = gr.Button("Search")
        output = gr.Textbox(label="Results")
        
        search_button.click(
            search_interface,
            inputs=[query_input, sentiment_checkbox, filename_input],
            outputs=output
        )
    
    with gr.Tab("Generate Answer"):
        question_input = gr.Textbox(label="Question")
        generate_button = gr.Button("Generate Answer")
        answer_output = gr.Textbox(label="Answer")
        
        generate_button.click(
            generate_interface,
            inputs=question_input,
            outputs=answer_output
        )

# Launch on a different port
if __name__ == "__main__":
    demo.launch(server_port=8000)




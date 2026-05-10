import json
import os
import re

def convert_dataset():
    input_file = "data/training/interview_dataset.json"
    output_file = "data/training/interview_dataset_structured.json"
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    structured_data = []
    
    for entry in data:
        output = entry.get("output", "")
        
        # If it's already a dict, keep it
        if isinstance(output, dict):
            structured_data.append(entry)
            continue
            
        # Parse the string output
        # Example: "Score: 4/10. Feedback: ... Seniority Signal: ..."
        score_match = re.search(r"Score:\s*(\d+)/10", output)
        total_score = int(score_match.group(1)) if score_match else 5
        
        feedback_parts = output.split("Feedback:")
        feedback_text = feedback_parts[1].strip() if len(feedback_parts) > 1 else output
        
        # Extract Seniority Signal if it exists in text
        signal_match = re.search(r"Seniority Signal:\s*(.*)", feedback_text, re.IGNORECASE)
        seniority_signal = signal_match.group(1).strip() if signal_match else "Mention advanced optimization techniques relevant to the topic."
        
        # Clean feedback text from signal
        feedback_clean = re.sub(r"Seniority Signal:\s*.*", "", feedback_text, flags=re.IGNORECASE).strip()
        feedback_clean = re.sub(r"\*\*Seniority Signal:\*\*\s*.*", "", feedback_clean, flags=re.IGNORECASE).strip()

        new_output = {
            "scores": {
                "technical_depth": total_score,
                "relevance": total_score,
                "clarity": total_score
            },
            "total_score": total_score,
            "feedback": feedback_clean,
            "star_method_compliance": "The candidate's use of the STAR method was inconsistent; focus on quantifying results.",
            "seniority_signal": seniority_signal,
            "curveball_question": "How would you ensure this solution scales to 100x the current load?",
            "ideal_answer": "A perfect answer would detail the architectural trade-offs, reference specific industry standards, and provide a clear, metrics-driven success story."
        }
        
        entry["output"] = new_output
        structured_data.append(entry)

    with open(output_file, "w") as f:
        json.dump(structured_data, f, indent=4)
    
    print(f"Successfully converted {len(structured_data)} entries to {output_file}")

if __name__ == "__main__":
    convert_dataset()

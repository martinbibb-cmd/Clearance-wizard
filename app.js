// Voice-to-Notes Application
// Uses Web Speech API for voice recognition and categorization

const voiceButton = document.getElementById('voice-button');
const rawTranscript = document.getElementById('raw-transcript');
const engineerOutput = document.getElementById('engineer-output').querySelector('ul');
const customerOutput = document.getElementById('customer-output').querySelector('ul');

// Check for Web Speech API Support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    voiceButton.textContent = "Voice Recognition Not Supported in this Browser.";
    voiceButton.disabled = true;
} else {
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Listen until manually stopped
    recognition.interimResults = true; // Show results as you speak

    let isRecording = false;

    voiceButton.onclick = () => {
        if (!isRecording) {
            recognition.start();
            isRecording = true;
            voiceButton.textContent = "🛑 Stop Recording & Summarize";
            voiceButton.style.backgroundColor = '#dc3545'; // Red
            rawTranscript.value = ""; // Clear old notes
            engineerOutput.innerHTML = "";
            customerOutput.innerHTML = "";
        } else {
            recognition.stop();
            isRecording = false;
            voiceButton.textContent = "🎙️ Start Recording";
            voiceButton.style.backgroundColor = '#ffc107'; // Yellow
            // The result logic (onresult) will handle the text one last time
        }
    };

    // --- VOICE-TO-TEXT HANDLING ---
    recognition.onresult = (event) => {
        let final_transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                final_transcript += event.results[i][0].transcript;
            } else {
                // Show interim results in the textarea
                rawTranscript.value = final_transcript + event.results[i][0].transcript;
            }
        }
        // Append final transcript chunks
        rawTranscript.value = final_transcript;
    };

    // --- SUMMARIZATION TRIGGERED ON STOP ---
    recognition.onend = () => {
        if (rawTranscript.value.trim() !== "") {
            // *** THIS IS WHERE YOUR CUSTOM LOGIC GOES ***
            const fullTranscript = rawTranscript.value.trim();
            const { engineerNotes, customerNotes } = categorizeAndSummarize(fullTranscript);

            displayNotes(engineerOutput, engineerNotes);
            displayNotes(customerOutput, customerNotes);
        }
    };

    // --- CUSTOM CATEGORIZATION/SUMMARIZATION FUNCTION ---
    function categorizeAndSummarize(text) {
        // Convert to lowercase for case-insensitive matching
        const lowerText = text.toLowerCase();
        
        // **Engineer Summary Logic (Waffle-free specifics)**
        let engineerNotes = [];
        if (lowerText.includes("new boiler model") || lowerText.includes("boiler model")) {
            engineerNotes.push("New Boiler: [Extract Model] installed in existing location. Flue route: [Extract Flue Details].");
        }
        if (lowerText.includes("gas route") || lowerText.includes("gas pipe")) {
            engineerNotes.push("Gas route requires 22mm run from meter via [Specify Route].");
        }
        if (lowerText.includes("scaffold") || lowerText.includes("working at heights")) {
            engineerNotes.push("Scaffold needed for flue termination. Area clear.");
        }
        if (lowerText.includes("flue") && !lowerText.includes("new boiler model")) {
            engineerNotes.push("Flue installation details: [Extract Flue Specifics].");
        }
        if (lowerText.includes("radiator") || lowerText.includes("heating")) {
            engineerNotes.push("Radiator/heating system: [Extract Details].");
        }
        if (lowerText.includes("water supply") || lowerText.includes("mains water")) {
            engineerNotes.push("Water supply: [Extract Connection Details].");
        }
        if (lowerText.includes("electrical") || lowerText.includes("power supply")) {
            engineerNotes.push("Electrical requirements: [Extract Specifications].");
        }
        if (lowerText.includes("access") || lowerText.includes("parking")) {
            engineerNotes.push("Site access and parking: [Extract Access Details].");
        }
        // Add many more of your specific keyword checks here...

        // **Customer Summary Logic (What, Why, How)**
        let customerNotes = [];
        customerNotes.push("What: We are installing a new, high-efficiency boiler.");
        customerNotes.push("Why: To save you money and improve reliability.");
        customerNotes.push("How: Work will take two days, noise expected during flue drilling.");
        
        // Add conditional customer notes based on detected keywords
        if (lowerText.includes("scaffold") || lowerText.includes("working at heights")) {
            customerNotes.push("Note: Scaffolding will be erected for safe access to the flue termination point.");
        }
        if (lowerText.includes("two days") || lowerText.includes("2 days")) {
            customerNotes.push("Timeline: Installation expected to complete within the specified timeframe.");
        }
        if (lowerText.includes("noise") || lowerText.includes("drilling")) {
            customerNotes.push("Please Note: Some noise will occur during drilling and installation work.");
        }
        // Add more customer-friendly summaries based on the raw text...

        return { engineerNotes, customerNotes };
    }

    // --- DISPLAY HELPER ---
    function displayNotes(outputElement, notesArray) {
        notesArray.forEach(note => {
            const li = document.createElement('li');
            li.textContent = note;
            outputElement.appendChild(li);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const clientFormContainer = document.getElementById('client-form-container');
    const clientInfoForm = document.getElementById('client-info-form');
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const policyRecommendations = document.getElementById('policy-recommendations');
    const recommendationsList = document.getElementById('recommendations-list');
    const backToFormButton = document.getElementById('back-to-form');
    const backToFormTopButton = document.getElementById('back-to-form-top');
    const switchToFormButton = document.getElementById('switch-to-form');
    const getRecommendationsButton = document.getElementById('get-recommendations');
    const addConditionButton = document.getElementById('add-condition');
    const addPrescriptionButton = document.getElementById('add-prescription');
    const addSurgeryButton = document.getElementById('add-surgery');
    const criminalHistorySelect = document.getElementById('criminal-history');
    const criminalHistoryDetails = document.getElementById('criminal-history-details');
    const stateSelect = document.getElementById('state');
    const coverageMinSlider = document.getElementById('coverage-min');
    const coverageMaxSlider = document.getElementById('coverage-max');
    const coverageMinValue = document.getElementById('coverage-min-value');
    const coverageMaxValue = document.getElementById('coverage-max-value');
    const companiesContainer = document.getElementById('companies-container');
    const companiesList = document.getElementById('companies-list');
    const policyTypeCheckboxes = document.querySelectorAll('input[name="policy_type[]"]');
    const ageInput = document.getElementById('age');

    // Chat history to maintain conversation context
    let chatHistory = [];

    // Client information gathered during chat or form
    let clientInfo = {};

    // Initialize state dropdown
    initializeStateDropdown();
    
    // Load and display available companies
    loadAvailableCompanies();
    
    // Add event listeners to policy type checkboxes
    policyTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Check if at least one checkbox is still selected
            const anyChecked = Array.from(policyTypeCheckboxes).some(cb => cb.checked);
            
            // If none are checked, re-check this one (require at least one selection)
            if (!anyChecked) {
                this.checked = true;
                alert('Please select at least one policy type');
            }
            
            // Update the companies list
            loadAvailableCompanies();
        });
    });

    // Event listeners
    clientInfoForm.addEventListener('submit', handleFormSubmit);
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    backToFormButton.addEventListener('click', () => {
        policyRecommendations.classList.add('hidden');
        clientFormContainer.classList.remove('hidden');
    });

    backToFormTopButton.addEventListener('click', () => {
        policyRecommendations.classList.add('hidden');
        clientFormContainer.classList.remove('hidden');
    });

    switchToFormButton.addEventListener('click', () => {
        chatContainer.classList.add('hidden');
        clientFormContainer.classList.remove('hidden');
    });

    // Coverage min slider event
    coverageMinSlider.addEventListener('input', () => {
        const minValue = parseInt(coverageMinSlider.value);
        const maxValue = parseInt(coverageMaxSlider.value);
        
        // Ensure min doesn't exceed max
        if (minValue > maxValue) {
            coverageMaxSlider.value = minValue;
            coverageMaxValue.textContent = `$${minValue.toLocaleString()}`;
        }
        
        coverageMinValue.textContent = `$${minValue.toLocaleString()}`;
    });
    
    // Coverage max slider event
    coverageMaxSlider.addEventListener('input', () => {
        const minValue = parseInt(coverageMinSlider.value);
        const maxValue = parseInt(coverageMaxSlider.value);
        
        // Ensure max doesn't go below min
        if (maxValue < minValue) {
            coverageMinSlider.value = maxValue;
            coverageMinValue.textContent = `$${maxValue.toLocaleString()}`;
        }
        
        coverageMaxValue.textContent = `$${maxValue.toLocaleString()}`;
    });

    // Auto-resize textarea as user types
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });

    // Medical conditions dynamic fields
    addConditionButton.addEventListener('click', () => {
        addMedicalConditionField();
    });

    // Add event delegation for remove buttons
    document.getElementById('medical-conditions').addEventListener('click', (e) => {
        if (e.target.closest('.remove-condition')) {
            const conditionItem = e.target.closest('.condition-item');
            if (document.querySelectorAll('.condition-item').length > 1) {
                conditionItem.remove();
            }
        }
    });

    // Prescriptions dynamic fields
    addPrescriptionButton.addEventListener('click', () => {
        addPrescriptionField();
    });

    document.getElementById('prescriptions').addEventListener('click', (e) => {
        if (e.target.closest('.remove-prescription')) {
            const prescriptionItem = e.target.closest('.prescription-item');
            if (document.querySelectorAll('.prescription-item').length > 1) {
                prescriptionItem.remove();
            }
        }
    });

    // Surgeries dynamic fields
    addSurgeryButton.addEventListener('click', () => {
        addSurgeryField();
    });

    document.getElementById('surgeries').addEventListener('click', (e) => {
        if (e.target.closest('.remove-surgery')) {
            const surgeryItem = e.target.closest('.surgery-item');
            if (document.querySelectorAll('.surgery-item').length > 1) {
                surgeryItem.remove();
            }
        }
    });

    // Show/hide criminal history details
    criminalHistorySelect.addEventListener('change', () => {
        if (criminalHistorySelect.value === 'yes') {
            criminalHistoryDetails.classList.remove('hidden');
        } else {
            criminalHistoryDetails.classList.add('hidden');
        }
    });

    // Add event listener for age input
    if (ageInput) {
        ageInput.addEventListener('change', loadAvailableCompanies);
        ageInput.addEventListener('input', function() {
            // Debounce for better performance - only update after typing stops
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(loadAvailableCompanies, 500);
        });
    }

    // Add event listeners for coverage sliders
    if (coverageMinSlider) {
        coverageMinSlider.addEventListener('change', loadAvailableCompanies);
        coverageMinSlider.addEventListener('input', function() {
            const minValue = parseInt(coverageMinSlider.value);
            const maxValue = parseInt(coverageMaxSlider.value);
            
            // Ensure min doesn't exceed max
            if (minValue > maxValue) {
                coverageMaxSlider.value = minValue;
                coverageMaxValue.textContent = `$${minValue.toLocaleString()}`;
            }
            
            coverageMinValue.textContent = `$${minValue.toLocaleString()}`;
            
            // Debounce the API call
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(loadAvailableCompanies, 500);
        });
    }
    
    if (coverageMaxSlider) {
        coverageMaxSlider.addEventListener('change', loadAvailableCompanies);
        coverageMaxSlider.addEventListener('input', function() {
            const minValue = parseInt(coverageMinSlider.value);
            const maxValue = parseInt(coverageMaxSlider.value);
            
            // Ensure max doesn't go below min
            if (maxValue < minValue) {
                coverageMinSlider.value = maxValue;
                coverageMinValue.textContent = `$${maxValue.toLocaleString()}`;
            }
            
            coverageMaxValue.textContent = `$${maxValue.toLocaleString()}`;
            
            // Debounce the API call
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(loadAvailableCompanies, 500);
        });
    }

    // Function to initialize the state dropdown
    function initializeStateDropdown() {
        const states = [
            { code: 'AL', name: 'Alabama' },
            { code: 'AK', name: 'Alaska' },
            { code: 'AZ', name: 'Arizona' },
            { code: 'AR', name: 'Arkansas' },
            { code: 'CA', name: 'California' },
            { code: 'CO', name: 'Colorado' },
            { code: 'CT', name: 'Connecticut' },
            { code: 'DE', name: 'Delaware' },
            { code: 'FL', name: 'Florida' },
            { code: 'GA', name: 'Georgia' },
            { code: 'HI', name: 'Hawaii' },
            { code: 'ID', name: 'Idaho' },
            { code: 'IL', name: 'Illinois' },
            { code: 'IN', name: 'Indiana' },
            { code: 'IA', name: 'Iowa' },
            { code: 'KS', name: 'Kansas' },
            { code: 'KY', name: 'Kentucky' },
            { code: 'LA', name: 'Louisiana' },
            { code: 'ME', name: 'Maine' },
            { code: 'MD', name: 'Maryland' },
            { code: 'MA', name: 'Massachusetts' },
            { code: 'MI', name: 'Michigan' },
            { code: 'MN', name: 'Minnesota' },
            { code: 'MS', name: 'Mississippi' },
            { code: 'MO', name: 'Missouri' },
            { code: 'MT', name: 'Montana' },
            { code: 'NE', name: 'Nebraska' },
            { code: 'NV', name: 'Nevada' },
            { code: 'NH', name: 'New Hampshire' },
            { code: 'NJ', name: 'New Jersey' },
            { code: 'NM', name: 'New Mexico' },
            { code: 'NY', name: 'New York' },
            { code: 'NC', name: 'North Carolina' },
            { code: 'ND', name: 'North Dakota' },
            { code: 'OH', name: 'Ohio' },
            { code: 'OK', name: 'Oklahoma' },
            { code: 'OR', name: 'Oregon' },
            { code: 'PA', name: 'Pennsylvania' },
            { code: 'RI', name: 'Rhode Island' },
            { code: 'SC', name: 'South Carolina' },
            { code: 'SD', name: 'South Dakota' },
            { code: 'TN', name: 'Tennessee' },
            { code: 'TX', name: 'Texas' },
            { code: 'UT', name: 'Utah' },
            { code: 'VT', name: 'Vermont' },
            { code: 'VA', name: 'Virginia' },
            { code: 'WA', name: 'Washington' },
            { code: 'WV', name: 'West Virginia' },
            { code: 'WI', name: 'Wisconsin' },
            { code: 'WY', name: 'Wyoming' },
            { code: 'DC', name: 'District of Columbia' }
        ];

        // Sort states alphabetically
        states.sort((a, b) => a.name.localeCompare(b.name));

        // Add options to select element
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state.code;
            option.textContent = state.name;
            stateSelect.appendChild(option);
        });
    }

    // Function to add a new medical condition field
    function addMedicalConditionField() {
        const conditionsContainer = document.getElementById('medical-conditions');
        const newCondition = document.createElement('div');
        newCondition.classList.add('condition-item');
        
        newCondition.innerHTML = `
            <select name="condition[]" class="condition-select">
                <option value="">Select Condition</option>
                <option value="none">None</option>
                <option value="high-blood-pressure">High Blood Pressure</option>
                <option value="diabetes">Diabetes</option>
                <option value="heart-disease">Heart Disease</option>
                <option value="cancer">Cancer</option>
                <option value="stroke">Stroke</option>
                <option value="copd">COPD</option>
                <option value="asthma">Asthma</option>
                <option value="other">Other (specify below)</option>
            </select>
            <input type="text" name="condition-details[]" placeholder="Details (year diagnosed, severity, etc.)" class="condition-details">
            <button type="button" class="remove-condition"><i class="fas fa-times"></i></button>
        `;
        
        conditionsContainer.appendChild(newCondition);
    }

    // Function to add a new prescription field
    function addPrescriptionField() {
        const prescriptionsContainer = document.getElementById('prescriptions');
        const newPrescription = document.createElement('div');
        newPrescription.classList.add('prescription-item');
        
        newPrescription.innerHTML = `
            <input type="text" name="prescription[]" placeholder="Medication name">
            <input type="text" name="prescription-dosage[]" placeholder="Dosage">
            <input type="text" name="prescription-frequency[]" placeholder="Frequency">
            <button type="button" class="remove-prescription"><i class="fas fa-times"></i></button>
        `;
        
        prescriptionsContainer.appendChild(newPrescription);
    }

    // Function to add a new surgery field
    function addSurgeryField() {
        const surgeriesContainer = document.getElementById('surgeries');
        const newSurgery = document.createElement('div');
        newSurgery.classList.add('surgery-item');
        
        newSurgery.innerHTML = `
            <input type="text" name="surgery[]" placeholder="Surgery type">
            <input type="month" name="surgery-date[]">
            <button type="button" class="remove-surgery"><i class="fas fa-times"></i></button>
        `;
        
        surgeriesContainer.appendChild(newSurgery);
    }

    // Function to handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Ensure at least one policy type is selected
        const policyTypeCheckboxes = document.querySelectorAll('input[name="policy_type[]"]:checked');
        if (policyTypeCheckboxes.length === 0) {
            alert('Please select at least one policy type preference');
            return;
        }
        
        // Collect form data
        const formData = new FormData(clientInfoForm);
        clientInfo = {
            sex: formData.get('sex'),
            age: parseInt(formData.get('age')),
            state: formData.get('state') || 'CA', // Default to CA if not provided
            height: parseInt(formData.get('height')) || 70, // Default height if not provided
            weight: parseInt(formData.get('weight')) || 170, // Default weight if not provided
            tobacco_status: formData.get('tobacco'),
            citizenship: formData.get('citizenship') || 'us-citizen',
            criminal_history: formData.get('criminal-history') || 'no',
            criminal_details: formData.get('criminal-details') || '',
            coverage_min: parseInt(formData.get('coverage-min')) || 100000,
            coverage_max: parseInt(formData.get('coverage-max')) || 500000
        };
        
        // Collect policy type preferences
        const policyTypes = [];
        policyTypeCheckboxes.forEach(checkbox => {
            policyTypes.push(checkbox.value);
        });
        clientInfo.policy_types = policyTypes;
        
        // Collect medical conditions
        const conditions = [];
        document.querySelectorAll('.condition-item').forEach((item, index) => {
            const conditionType = formData.getAll('condition[]')[index];
            if (conditionType && conditionType !== 'none') {
                conditions.push({
                    type: conditionType,
                    details: formData.getAll('condition-details[]')[index] || ''
                });
            }
        });
        clientInfo.medical_conditions = conditions;
        
        // Collect prescriptions
        const prescriptions = [];
        document.querySelectorAll('.prescription-item').forEach((item, index) => {
            const medicationName = formData.getAll('prescription[]')[index];
            if (medicationName) {
                prescriptions.push({
                    name: medicationName,
                    dosage: formData.getAll('prescription-dosage[]')[index] || '',
                    frequency: formData.getAll('prescription-frequency[]')[index] || ''
                });
            }
        });
        clientInfo.prescriptions = prescriptions;
        
        // Collect surgeries
        const surgeries = [];
        document.querySelectorAll('.surgery-item').forEach((item, index) => {
            const surgeryType = formData.getAll('surgery[]')[index];
            if (surgeryType) {
                surgeries.push({
                    type: surgeryType,
                    date: formData.getAll('surgery-date[]')[index] || ''
                });
            }
        });
        clientInfo.surgeries = surgeries;
        
        // Calculate BMI if height and weight are provided
        if (clientInfo.height && clientInfo.weight) {
            const heightInMeters = clientInfo.height * 0.0254;
            const weightInKg = clientInfo.weight * 0.453592;
            clientInfo.bmi = (weightInKg / (heightInMeters * heightInMeters)).toFixed(1);
        }
        
        console.log('Client info collected:', clientInfo);
        
        // Get recommendations
        await getRecommendations();
    }

    // Function to send user message and get response
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessageToChat('user', message);
        
        // Add to chat history
        chatHistory.push({ role: 'user', content: message });
        
        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Show typing indicator
        const typingIndicator = addTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message, 
                    chat_history: chatHistory 
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
            
            // Add assistant response to chat
            addMessageToChat('assistant', data.response);
            
            // Add to chat history
            chatHistory.push({ role: 'assistant', content: data.response });
            
            // Check if we should show recommendations
            if (data.response.includes("recommend") && data.response.includes("policies")) {
                setTimeout(getRecommendations, 1000);
            }
            
            // Extract client information from message
            extractClientInfo(message);
            
        } catch (error) {
            console.error('Error:', error);
            
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
            
            // Add error message
            addMessageToChat('assistant', 'Sorry, I encountered an error. Please try again.');
        }
        
        // Scroll to bottom
        scrollToBottom();
    }

    // Function to add a message to the chat
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${role}-message`);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        
        messageContent.appendChild(paragraph);
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        scrollToBottom();
    }

    // Function to add typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'assistant-message', 'typing-indicator');
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        const dots = document.createElement('div');
        dots.classList.add('typing-dots');
        dots.innerHTML = '<span></span><span></span><span></span>';
        
        messageContent.appendChild(dots);
        typingDiv.appendChild(messageContent);
        chatMessages.appendChild(typingDiv);
        
        scrollToBottom();
        return typingDiv;
    }

    // Function to extract client information from chat messages
    function extractClientInfo(message) {
        // This is a simple implementation - in a real app, this would be done on the backend
        // with more sophisticated NLP
        
        const messageLower = message.toLowerCase();
        
        // Extract name
        if (messageLower.includes('my name is')) {
            const nameMatch = message.match(/my name is\s+([A-Za-z\s]+)/i);
            if (nameMatch && nameMatch[1]) {
                clientInfo.name = nameMatch[1].trim();
            }
        }
        
        // Extract age
        if (messageLower.includes('i am') && messageLower.includes('years old')) {
            const ageMatch = message.match(/i am\s+(\d+)\s+years old/i);
            if (ageMatch && ageMatch[1]) {
                clientInfo.age = parseInt(ageMatch[1]);
            }
        }
        
        // Extract sex/gender
        if (messageLower.includes('male') || messageLower.includes('female')) {
            if (messageLower.includes('female')) {
                clientInfo.sex = 'female';
            } else if (messageLower.includes('male')) {
                clientInfo.sex = 'male';
            }
        }
        
        // Extract state
        const statePattern = /(?:i live in|i'm from|i am from|in)\s+([A-Za-z\s]+)(?:,|\s+state)/i;
        const stateMatch = message.match(statePattern);
        if (stateMatch && stateMatch[1]) {
            clientInfo.state = stateMatch[1].trim();
        }
        
        // Extract height and weight
        const heightPattern = /(\d+)\s*(?:feet|foot|ft)(?:\s+(\d+)\s*(?:inches|inch|in))?/i;
        const heightMatch = message.match(heightPattern);
        if (heightMatch) {
            const feet = parseInt(heightMatch[1]);
            const inches = heightMatch[2] ? parseInt(heightMatch[2]) : 0;
            clientInfo.height = feet * 12 + inches;
        }
        
        const weightPattern = /(\d+)\s*(?:pounds|pound|lbs|lb)/i;
        const weightMatch = message.match(weightPattern);
        if (weightMatch) {
            clientInfo.weight = parseInt(weightMatch[1]);
        }
        
        // Extract tobacco status
        if (messageLower.includes('smoke') || messageLower.includes('tobacco')) {
            if (messageLower.includes("don't smoke") || messageLower.includes("do not smoke") || messageLower.includes("non-smoker")) {
                clientInfo.tobacco_status = 'non-smoker';
            } else if (messageLower.includes("used to smoke") || messageLower.includes("quit smoking")) {
                clientInfo.tobacco_status = 'former-smoker';
            } else if (messageLower.includes("i smoke") || messageLower.includes("smoker")) {
                clientInfo.tobacco_status = 'smoker';
            }
        }
        
        // Extract medical conditions
        if (messageLower.includes('condition') || messageLower.includes('disease') || messageLower.includes('diagnosed')) {
            const conditions = [];
            
            if (messageLower.includes('high blood pressure') || messageLower.includes('hypertension')) {
                conditions.push({ type: 'high-blood-pressure', details: '' });
            }
            
            if (messageLower.includes('diabetes')) {
                conditions.push({ type: 'diabetes', details: '' });
            }
            
            if (messageLower.includes('heart disease') || messageLower.includes('heart attack')) {
                conditions.push({ type: 'heart-disease', details: '' });
            }
            
            if (messageLower.includes('cancer')) {
                conditions.push({ type: 'cancer', details: '' });
            }
            
            if (messageLower.includes('stroke')) {
                conditions.push({ type: 'stroke', details: '' });
            }
            
            if (conditions.length > 0) {
                clientInfo.medical_conditions = conditions;
            }
        }
        
        console.log('Updated client info from chat:', clientInfo);
    }

    // Function to get policy recommendations
    async function getRecommendations() {
        try {
            // Add some reasonable defaults if missing from chat extraction
            const defaultedClientInfo = {
                ...clientInfo,
                age: clientInfo.age || 35,
                sex: clientInfo.sex || 'male',
                state: clientInfo.state || 'CA',
                tobacco_status: clientInfo.tobacco_status || 'non-smoker',
                medical_conditions: clientInfo.medical_conditions || [],
                bmi: clientInfo.bmi || 25,
                coverage_min: clientInfo.coverage_min || parseInt(coverageMinSlider.value) || 100000,
                coverage_max: clientInfo.coverage_max || parseInt(coverageMaxSlider.value) || 500000
            };
            
            // Request recommendations from backend
            const response = await fetch('/api/recommend-policy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(defaultedClientInfo)
            });
            
            const data = await response.json();
            
            // Check if we have recommendations
            if (data.recommendations && data.recommendations.length > 0) {
                // Clear previous recommendations
                recommendationsList.innerHTML = '';
                
                // Add recommendation summary at the top
                if (data.summary) {
                    const summaryDiv = document.createElement('div');
                    summaryDiv.classList.add('recommendation-summary');
                    summaryDiv.textContent = data.summary;
                    recommendationsList.appendChild(summaryDiv);
                }
                
                // Add recommendations to the list
                data.recommendations.forEach(policy => {
                    const policyCard = createPolicyCard(policy);
                    recommendationsList.appendChild(policyCard);
                });
                
                // If we have recommendations but added a coverage range filter, show it
                if (data.recommendations.length > 0) {
                    const minCoverage = defaultedClientInfo.coverage_min.toLocaleString();
                    const maxCoverage = defaultedClientInfo.coverage_max.toLocaleString();
                    
                    const coverageFilterInfo = document.createElement('div');
                    coverageFilterInfo.classList.add('coverage-filter-info');
                    coverageFilterInfo.textContent = `Showing policies with coverage between $${minCoverage} - $${maxCoverage}`;
                    
                    // Insert after the summary
                    const summary = recommendationsList.querySelector('.recommendation-summary');
                    if (summary) {
                        recommendationsList.insertBefore(coverageFilterInfo, summary.nextSibling);
                    } else {
                        recommendationsList.insertBefore(coverageFilterInfo, recommendationsList.firstChild);
                    }
                }
                
                // Hide client form and show recommendations
                clientFormContainer.classList.add('hidden');
                chatContainer.classList.add('hidden');
                policyRecommendations.classList.remove('hidden');
            } else {
                // If no recommendations, show a message
                const noRecommendations = document.createElement('div');
                noRecommendations.classList.add('no-recommendations');
                noRecommendations.textContent = "I couldn't find any policy recommendations based on your information. Please review your details and try again.";
                
                recommendationsList.innerHTML = '';
                recommendationsList.appendChild(noRecommendations);
                
                // Hide client form and show recommendations
                clientFormContainer.classList.add('hidden');
                chatContainer.classList.add('hidden');
                policyRecommendations.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error getting recommendations:', error);
            alert('Sorry, I encountered an error while finding policy recommendations. Please try again.');
        }
    }

    // Function to create a policy card element
    function createPolicyCard(policy) {
        const card = document.createElement('div');
        card.classList.add('policy-card');
        
        // Create header with company name and match score
        const header = document.createElement('div');
        header.classList.add('policy-header');
        
        const company = document.createElement('div');
        company.classList.add('policy-company');
        company.textContent = policy.company_name;
        
        const score = document.createElement('div');
        score.classList.add('match-score');
        score.textContent = `${Math.round(policy.match_score)}% Match`;
        
        header.appendChild(company);
        header.appendChild(score);
        
        // Create policy name and type
        const name = document.createElement('h3');
        name.classList.add('policy-name');
        name.textContent = policy.policy_name;
        
        const type = document.createElement('div');
        type.classList.add('policy-type');
        type.textContent = formatPolicyType(policy.policy_type);
        
        // Create policy details
        const details = document.createElement('div');
        details.classList.add('policy-details');
        
        // Coverage detail
        const coverageDetail = document.createElement('div');
        coverageDetail.classList.add('detail-item');
        
        const coverageLabel = document.createElement('div');
        coverageLabel.classList.add('detail-label');
        coverageLabel.textContent = 'Coverage Range';
        
        const coverageValue = document.createElement('div');
        coverageValue.classList.add('detail-value');
        coverageValue.textContent = policy.coverage_range;
        
        coverageDetail.appendChild(coverageLabel);
        coverageDetail.appendChild(coverageValue);
        
        details.appendChild(coverageDetail);
        
        // Add notes if they exist
        if (policy.notes && policy.notes.length > 0) {
            const notesContainer = document.createElement('div');
            notesContainer.classList.add('policy-notes');
            
            const notesLabel = document.createElement('div');
            notesLabel.classList.add('detail-label');
            notesLabel.textContent = 'Notes';
            
            const notesList = document.createElement('ul');
            notesList.classList.add('notes-list');
            
            policy.notes.forEach(note => {
                const noteItem = document.createElement('li');
                noteItem.textContent = note;
                
                // Check if this is a medical-related note
                if (note.includes("cancer:") || 
                    note.includes("diabetes:") || 
                    note.includes("heart") || 
                    note.includes("blood pressure") || 
                    note.includes("medical") || 
                    note.includes("health") ||
                    note.includes("condition") ||
                    note.includes("diagnosed") ||
                    note.includes("rating") ||
                    note.includes("Declined")) {
                    noteItem.classList.add('medical-note');
                }
                
                notesList.appendChild(noteItem);
            });
            
            notesContainer.appendChild(notesLabel);
            notesContainer.appendChild(notesList);
            
            // Add after details
            card.appendChild(header);
            card.appendChild(name);
            card.appendChild(type);
            card.appendChild(details);
            card.appendChild(notesContainer);
        } else {
            // Add without notes
            card.appendChild(header);
            card.appendChild(name);
            card.appendChild(type);
            card.appendChild(details);
        }
        
        // Create features list
        const featuresContainer = document.createElement('div');
        
        const featuresLabel = document.createElement('div');
        featuresLabel.classList.add('detail-label');
        featuresLabel.textContent = 'Features';
        
        const featuresList = document.createElement('div');
        featuresList.classList.add('features-list');
        
        policy.features.forEach(feature => {
            const featureItem = document.createElement('span');
            featureItem.classList.add('feature');
            featureItem.textContent = feature;
            featuresList.appendChild(featureItem);
        });
        
        featuresContainer.appendChild(featuresLabel);
        featuresContainer.appendChild(featuresList);
        
        // Add features container
        card.appendChild(featuresContainer);
        
        return card;
    }

    // Helper function to format policy type for display
    function formatPolicyType(type) {
        if (type === "term_life") {
            return "Term Life Insurance";
        } else if (type === "whole_life") {
            return "Whole Life Insurance";
        } else if (type === "universal_life") {
            return "Universal Life Insurance";
        } else if (type === "final_expense") {
            return "Final Expense Insurance";
        }
        return type;
    }

    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to load and display available insurance companies
    function loadAvailableCompanies() {
        // First update the info text
        const companiesInfo = companiesContainer.querySelector('.companies-info');
        companiesInfo.textContent = "Loading available insurance companies...";
        
        // Get selected policy types
        const selectedPolicyTypes = Array.from(
            document.querySelectorAll('input[name="policy_type[]"]:checked')
        ).map(checkbox => checkbox.value);
        
        // Get current age value
        const ageInput = document.getElementById('age');
        const age = ageInput.value ? parseInt(ageInput.value) : null;
        
        // Get current coverage range values
        const coverageMin = coverageMinSlider ? parseInt(coverageMinSlider.value) : null;
        const coverageMax = coverageMaxSlider ? parseInt(coverageMaxSlider.value) : null;
        
        // Build the query parameters
        const params = new URLSearchParams();
        if (age) {
            params.append('age', age);
        }
        if (coverageMin) {
            params.append('coverage_min', coverageMin);
        }
        if (coverageMax) {
            params.append('coverage_max', coverageMax);
        }
        if (selectedPolicyTypes.length > 0) {
            params.append('policy_types', selectedPolicyTypes.join(','));
        }
        
        // Create a simple API endpoint to fetch companies
        fetch(`/api/companies?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Filter companies based on selected policy types
                let filteredCompanies = data.companies;
                
                // Update the info text with the count
                const companyCount = filteredCompanies.length;
                if (companyCount === 0) {
                    companiesInfo.textContent = 'No insurance companies found for selected criteria.';
                    companiesList.innerHTML = '';
                    return;
                }
                
                const policyCount = filteredCompanies.reduce((total, company) => total + company.policy_count, 0);
                
                // Customize the message based on what filters are applied
                let infoMessage = `${companyCount} insurance companies with ${policyCount} policies`;
                if (age) {
                    infoMessage += ` for age ${age}`;
                }
                if (coverageMin || coverageMax) {
                    const formattedMin = coverageMin ? `$${coverageMin.toLocaleString()}` : "any";
                    const formattedMax = coverageMax ? `$${coverageMax.toLocaleString()}` : "any";
                    infoMessage += ` with coverage ${formattedMin} to ${formattedMax}`;
                }
                if (selectedPolicyTypes.length > 0) {
                    const typeNames = selectedPolicyTypes.map(formatPolicyType).join(', ');
                    infoMessage += ` offering ${typeNames}`;
                }
                companiesInfo.textContent = infoMessage + ':';
                
                // Clear the list first
                companiesList.innerHTML = '';
                
                // Add each company to the list
                filteredCompanies.forEach(company => {
                    const companyItem = document.createElement('div');
                    companyItem.classList.add('company-item');
                    
                    // Build the company item with name and icon
                    let companyHTML = `
                        <i class="fas fa-building company-icon"></i>
                        ${company.name}
                    `;
                    
                    // Add age range if available
                    if (company.age_range) {
                        companyHTML += `<span class="company-age-range">Ages ${company.age_range}</span>`;
                    }
                    
                    // Add coverage range if available
                    if (company.coverage_range) {
                        companyHTML += `<span class="company-coverage-range">${company.coverage_range}</span>`;
                    }
                    
                    companyItem.innerHTML = companyHTML;
                    
                    // If the company has a policy count, add a badge
                    if (company.policy_count) {
                        const policyBadge = document.createElement('span');
                        policyBadge.classList.add('companies-badge');
                        policyBadge.textContent = `${company.policy_count} policies`;
                        companyItem.appendChild(policyBadge);
                    }
                    
                    companiesList.appendChild(companyItem);
                });
            })
            .catch(error => {
                console.error('Error fetching companies:', error);
                // Provide a fallback message
                companiesInfo.textContent = 'Using all available insurance companies for recommendations.';
                
                // Create a generic "all companies" message
                companiesList.innerHTML = `
                    <div class="company-item">
                        <i class="fas fa-building company-icon"></i>
                        All available insurance carriers
                    </div>
                `;
            });
    }
}); 
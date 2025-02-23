let selectedCircle = null;

function pickLimiterPattern(buttonId) {
    const buttons = document.querySelectorAll(".limiterPattern-containter button");

    // Remove active class from all buttons
    buttons.forEach(btn => btn.className = "pure-button");
    
    // Add active class to the clicked button
    document.getElementById(buttonId).className = "pure-button pure-button-active";
    
    // Send API request with the selected button's ID
    fetch("/shiftLights/limitPattern", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ pattern: buttonId })
    }).catch(error => console.error("Error sending API request:", error));
}

function pickPin(id) {
    
}

function pickColor(circle) {
    selectedCircle = circle;  // Store the clicked circle
    
    // Get the position of the clicked circle on the screen
    const rect = circle.getBoundingClientRect();
    
    // Get the color picker element
    const colorPicker = document.getElementById('colorPicker');
    
    // Position the color picker at the clicked circle's location
    colorPicker.style.left = `${rect.left}px`;  // X position
    colorPicker.style.top = `${rect.top + rect.height + 10}px`;  // Y position (10px below the circle)

    // Show the color picker before triggering the click event
    colorPicker.style.display = 'block';

    // Trigger a click event to show the color picker
    colorPicker.click();
}

function changeColor(event) {
    // Change the circle's background color
    const newColor = event.target.value;
    selectedCircle.style.backgroundColor = newColor;

    // Prepare the request payload
    const requestBody = {
        color: newColor
    };

    // Send a POST request to your API
    fetch(`/shiftLights/${selectedCircle.id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to update color: ${response.statusText}`);
        }
        return response;
    })
    .then(data => console.log("Color update successful:", data))
    .catch(error => console.error("Error updating color:", error));
}

function addCirle(container,color,id) {
    const circle = document.createElement('div');
    circle.className = 'circle';
    circle.id = `${id}`;
    circle.onclick = function() { pickColor(this); };

    // Convert color values to CSS format (assuming they are 0-255)
    const red = color.red;
    const green = color.green;
    const blue = color.blue;
    circle.style.backgroundColor = `rgb(${red}, ${green}, ${blue})`;
    
    container.appendChild(circle);  // Append to shiftLight-container
}

document.addEventListener("DOMContentLoaded", () => {
    fetch('/shiftLights')  
        .then(response => response.json())
        .then(data => {
            const circleContainer = document.querySelector('.shiftLight-container');
            
            // shift light cirlces
            data.ShiftLights.forEach(light => {
                addCirle(circleContainer,light.color,light.id)
            });

            
            // limiter circle
            addCirle(document.querySelector('.limiterColor-container'),data.LimiterColor.color,data.LimiterColor.id)
            
            const limiterContainer =  document.querySelector('.limiterPattern-containter');
            //limiter pattern buttons
            selected = data.LimiterPattern.selected
            data.LimiterPattern.patterns.forEach(pattern => {
                const button = document.createElement('button');
                button.id = pattern;
                button.innerText = pattern
                button.onclick = function() { pickLimiterPattern(pattern); };

                if (pattern == selected) {
                    button.className = "pure-button pure-button-active";
                } else {
                    button.className = "pure-button";
                }
                limiterContainer.appendChild(button);

            })

        })
        .catch(error => console.error('Error fetching shiftLights:', error));

        fetch('/pins')  
        .then(response => response.json())
        .then(data => {
            pinSelectors = document.querySelectorAll('.pinSelector-container');

            pinSelectors.forEach(pinSelector => {
                console.log(pinSelector.innerText); // Do something with each container
            });
            
            
            //limiter pattern buttons
            selected = data.LimiterPattern.selected
            data.LimiterPattern.patterns.forEach(pattern => {
                const button = document.createElement('button');
                button.id = pattern;
                button.innerText = pattern
                button.onclick = function() { pickLimiterPattern(pattern); };

                if (pattern == selected) {
                    button.className = "pure-button pure-button-active";
                } else {
                    button.className = "pure-button";
                }
                limiterContainer.appendChild(button);

            })

        })
        .catch(error => console.error('Error fetching shiftLights:', error));
});
// Function to toggle between showing the pause and resume buttons
function togglePauseResumeButton(vmName, status) {
    const pauseResumeForm = document.getElementById(`pause-resume-${vmName}`);
    const pauseButton = pauseResumeForm.querySelector('.pause-button');
    const resumeButton = pauseResumeForm.querySelector('.resume-button');

    if (status === 'Paused') {
        pauseButton.style.display = 'none';
        resumeButton.style.display = 'inline-block';
    } else {
        pauseButton.style.display = 'inline-block';
        resumeButton.style.display = 'none';
    }
}

// Function to start the virtual machine
function startVM(vmName) {
    fetch(`/start-vm/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ vm_name: vmName })
    }).then(response => {
        if (response.ok) {
            const messageElement = document.getElementById(`status-${vmName}`);
            console.log('dddd');
            messageElement.textContent = `Starting VM ${vmName} request sent.`;
            messageElement.style.display = 'block';
        } else {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Failed to start VM ${vmName}: ${response.statusText}`;
            messageElement.style.display = 'block';
        }
    }).catch(error => {
        const messageElement = document.getElementById(`status-${vmName}`);
        messageElement.textContent = `Failed to start VM ${vmName}: ${error.message}`;
        messageElement.style.display = 'block';
    });
}

// Function to stop the virtual machine
function stopVM(vmName) {
    fetch(`/stop-vm/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ vm_name: vmName })
    }).then(response => {
        if (response.ok) {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Stopping VM ${vmName} request sent.`;
            messageElement.style.display = 'block';
            messageElement.textContent = `iam hereeee`;

        } else {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Failed to stop VM ${vmName}: ${response.statusText}`;
            messageElement.style.display = 'block';
        }
    }).catch(error => {
        const messageElement = document.getElementById(`status-${vmName}`);
        messageElement.textContent = `Failed to stop VM ${vmName}: ${error.message}`;
        messageElement.style.display = 'block';
    });
}

// Function to pause the virtual machine
function pauseVM(vmName) {
    fetch(`/pause-vm/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ vm_name: vmName })
    }).then(response => {
        if (response.ok) {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Pausing VM ${vmName} request sent.`;
            messageElement.style.display = 'block';
            togglePauseResumeButton(vmName, 'Paused'); // Update button display
        } else {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Failed to pause VM ${vmName}: ${response.statusText}`;
            messageElement.style.display = 'block';
        }
    }).catch(error => {
        const messageElement = document.getElementById(`status-${vmName}`);
        messageElement.textContent = `Failed to pause VM ${vmName}: ${error.message}`;
        messageElement.style.display = 'block';
    });
}

// Function to resume the virtual machine
function resumeVM(vmName) {
    fetch(`/resume-vm/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ vm_name: vmName })
    }).then(response => {
        if (response.ok) {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Resuming VM ${vmName} request sent.`;
            messageElement.style.display = 'block';
            togglePauseResumeButton(vmName, 'Resumed'); // Update button display
        } else {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Failed to resume VM ${vmName}: ${response.statusText}`;
            messageElement.style.display = 'block';
        }
    }).catch(error => {
        const messageElement = document.getElementById(`status-${vmName}`);
        messageElement.textContent = `Failed to resume VM ${vmName}: ${error.message}`;
        messageElement.style.display = 'block';
    });
}

// Function to forcefully shut down the virtual machine
function forceOffVM(vmName) {
    fetch(`/force-off-vm/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ vm_name: vmName })
    }).then(response => {
        if (response.ok) {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `ForceOFF VM ${vmName} request sent.`;
            messageElement.style.display = 'block';
        } else {
            const messageElement = document.getElementById(`status-${vmName}`);
            messageElement.textContent = `Failed to ForceOFF VM ${vmName}: ${response.statusText}`;
            messageElement.style.display = 'block';
        }
    }).catch(error => {
        const messageElement = document.getElementById(`status-${vmName}`);
        messageElement.textContent = `Failed to ForceOFF VM ${vmName}: ${error.message}`;
        messageElement.style.display = 'block';
    });
}




// Function to get CSRF token from cookies
function getCookie(name) {
    console.log("ddddddd");
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    var text = "Caring for your animals made easier with AI";
    var index = 0;
    var speed = 100; // Speed of typing in milliseconds

    function typeWriter() {
        if (index < text.length) {
            document.getElementById("typing-text").innerHTML += text.charAt(index);
            index++;
            setTimeout(typeWriter, speed);
        }
    }

    typeWriter();
});

<?php
// PHP
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);

// Vulnerable code
if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
    echo "The file has been uploaded.";
} else {
    echo "Sorry, there was an error uploading your file.";
}

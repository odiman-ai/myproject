if (!$b_result) {
    echo json_encode(["error" => "Beneficiary not found"]);
    exit;
}

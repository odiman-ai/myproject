@app.get("/beneficiaries/{beneficiary_id}", response_model=schemas.Beneficiary)
def get_beneficiary(beneficiary_id: int, db: Session = Depends(get_db)):
    beneficiary = db.query(models.Beneficiary).filter(models.Beneficiary.id == beneficiary_id).first()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return beneficiary   # ✅ Pydantic can now map ORM → schema

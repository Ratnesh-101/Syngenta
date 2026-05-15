class SignalIngest(BaseModel):
    entity_id:      str
    signal_type:    str                 # "pest" | "weather" | "inventory" etc.
    severity:       Optional[str]       # "low" | "medium" | "high" | "critical"
    payload:        dict                # raw signal data, flexible
    source:         str                 # "api" | "manual" | "erp"
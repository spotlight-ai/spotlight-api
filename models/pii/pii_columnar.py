from db import db

class ColumnarPIIModel(db.Model):
    __tablename__ = "pii_columnar"
    __tableargs__ = db.UniqueConstraint(
        "columnar_pii_id", "dataset_id","column_index"
    )
    columnar_pii_id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.dataset_id", ondelete="cascade")
    )
    pii_id = db.Column(db.Integer, db.ForeignKey("pii_marker_base.pii_id", ondelete="cascade"))
    # pii_type = db.Column(db.String, nullable=False)
    column_index = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float,nullable=False)
    
    def __init__(self, dataset_id, pii_id, column_index, confidence):
        
        self.dataset_id = dataset_id
        self.pii_id=pii_id
        # self.pii_type=pii_type
        self.column_index = column_index
        self.confidence=confidence
    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.columnar_pii_id}, {self.dataset_id}, {self.pii_id}, {self.col}, "
            f"{self.confidence}%)"
        )
    
    def __str__(self):
        return f"PII {self.pii_id} ({self.column_index} - {self.confidence}% confidence)"   
         

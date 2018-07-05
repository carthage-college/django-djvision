from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import SmallInteger, Integer, Boolean, Column, DateTime, Text
from djtools.fields import NOW

Base = declarative_base()


class ProvisioningBatchRec(Base):
    __tablename__ = 'cc_provisioning_batch_rec'

    batch_no = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=NOW, nullable=False)
    total = Column(Integer)
    sitrep = Column(SmallInteger)
    notes = Column(Text)

    def __repr__(self):
        return str(self.batch_no)

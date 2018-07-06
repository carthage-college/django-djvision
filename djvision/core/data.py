from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey
from sqlalchemy import Integer, SmallInteger, String, Text
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


class ProvisioningDetailRec(Base):
    __tablename__ = 'cc_provisioning_detail_rec'

    detail_no = Column(Integer, primary_key=True, autoincrement=True)
    # foreign key to cc_provisioning_batch_rec
    batch = Column(Integer, ForeignKey(ProvisioningBatchRec.batch_no))
    created_at = Column(DateTime, default=NOW, nullable=False)
    username = Column(String)
    last_name = Column(String)
    first_name = Column(String)
    # foreign key to id_rec
    id = Column(Integer, nullable=False)
    faculty = Column(String)
    staff = Column(String)
    student = Column(String)
    retire = Column(String)
    birth_date = Column(Date)
    postal_code = Column(String)
    account = Column(String)
    proxid = Column(Integer)
    phone_ext = Column(String)
    departments = Column(String)
    csv = Column(Text)
    notes = Column(Text)

    # relationships
    batch_rec = relationship('ProvisioningBatchRec', foreign_keys='ProvisioningDetailRec.batch')

    def __repr__(self):
        return str(self.username)

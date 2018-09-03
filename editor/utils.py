from .models import Document


# сформировать json из документа
def document2json(document: Document):
	assert isinstance(document, Document)

	dview = dict()
	dview["creator"] = document.creator
	dview["details"] = document.details
	dview["name"] = document.name
	dview["is_active"] = document.is_active
	

from google.cloud.firestore_v1.base_query import FieldFilter,Or
#EXEPLU
# data = {
#     "Author": "Ioan Slavici",
#     "Genre": "Drama",
#     "Image": "\\rand1",
#     "Name": "Mara"
# }
# qr.insert_document(db,'Book',data)
def insert_document(db,collection,data, return_id = False):
    doc_ref = db.collection(collection).document()
    doc_ref.set(data)

    if return_id:
        return doc_ref.id
#EXEMPLU qr.update_existing_document(db,'Book',id,"Name","Mara")
def update_existing_document(db,collection,docID,updated_field,updated_value):

    # Get the reference to the collection

    collection_ref = db.collection(collection)


    # Get the document you want to update by its ID

    doc_ref = collection_ref.document(docID)


    # Update the document

    doc_ref.update({

        updated_field: updated_value

    })



    # Get the document you want to update by its ID

    #doc_ref = collection_ref.document('your_document_id')


    # Update the document

    #doc_ref.update({

    #    'field_to_update': 'new_value'

    #})
#EXEMPLU qr.get_all_docs(db,'Book')
def get_all_docs(db,collectionName):

    # Get the reference to the collection

    #collection_ref = db.collection(collectionName)


    docs = (

            db.collection(collectionName)

            .stream()

        )


    # Iterate over the documents and store their IDs and data in a list

    documents_list = []

    for doc in docs:

        doc_data = doc.to_dict()

        doc_data['id'] = doc.id

        # doc_data['docData'] = doc._data

        #print(doc._data)

        documents_list.append(doc_data)
    
    return documents_list 



def get_document(db,collection_name, document_id):

    doc_ref = db.collection(collection_name).document(document_id)

    print(doc_ref)

    doc = doc_ref.get()

    print(doc)

    if doc.exists:

        return doc.to_dict()

    else:

        print(f"Document '{document_id}' not found in collection '{collection_name}'.")

        return None

   
# mara = qr.get_documents_with_status(db,'Book','Name','==','Mara')
# qr.delete_document(db,"Book",mara[0][1]) mara[0][1] e fix id ul ala pe care il are elementul, cheia primara
def delete_document(db,collection_name, document_id):

    try:

        doc_ref = db.collection(collection_name).document(document_id)

        doc_ref.delete()

        print(f"Document with ID {document_id} deleted successfully.")

    except Exception as e:

        print(f"Error deleting document: {str(e)}")

#EXEMPLU get_documents_with_status(db,'Book','Name','==','Baltagul')
def get_documents_with_status(db,collection_name,status_name,status_clause, status_value):

    try:

        doc_ref = db.collection(collection_name)

       

        #make your query
        query = doc_ref.where(filter=FieldFilter(status_name, status_clause, status_value))


        #stream for results

        docs = query.stream()

        documents = []

        for doc in docs:
            documents.append([doc.to_dict(),doc.id])


       


       

       

        return documents
    
    except Exception as e:

        print(f"Error retrieving documents: {str(e)}")

#inca nu o fac pe asta sa vedem daca avem nevoie
def get_different_status(db,collection_name, status_value1, status_value2):

    try:

        doc_ref = db.collection(collection_name)

        filter_todo = FieldFilter("status", "==", status_value1)

        filter_done = FieldFilter("status", "==", status_value2)


        # Create the union filter of the two filters (queries)

        or_filter = Or(filters=[filter_todo, filter_done])


        # Execute the query

        docs = doc_ref.where(filter=or_filter).stream()


       


       

       

        return docs

    except Exception as e:

        print(f"Error retrieving documents: {str(e)}")


# #READ DATA

# get_all_docs("tasksCollection")

# print(get_document('tasksCollection','flfWqunWhohtaJ7OpSzO' ))

# get_documents_with_status("tasksCollection", "TODO")

# get_different_status("tasksCollection", "TODO", "done")


# #UPDATE DATA

# update_existing_document("flfWqunWhohtaJ7OpSzO")


# #DELETE DATA

# delete_document('tasksCollection','flfWqunWhohtaJ7OpSzO')
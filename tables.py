from flask_table import Table, Col, LinkCol
 
class Results(Table):
    emp_id = Col('emp_id')
    job_title = Col('job_title')
    salary = Col('salary')
    edit = LinkCol('Edit', 'edit_view', url_kwargs=dict(id='emp_id'))
    delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='emp_id'))

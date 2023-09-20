@roi.route('/delete/<id>', methods=['POST','GET'])
@login_required
def prop_delete(id):
    db.session.execute(delete(Property).where(Property.prop_id == id))
    db.session.commit()
    return redirect('/properties')
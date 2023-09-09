    inc_total = db.session.execute(text(f'select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = {current_user.user_id}'))
        roi= calc_roi(props[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
        roi = roi*100
        roi_f = "%.2f" % roi+"%"
        print(f"R
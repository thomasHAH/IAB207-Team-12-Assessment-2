@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        flash("You are not authorised to edit this event.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    form = EventForm()
    cancel_form = CancelForm()  # <-- new

    # Handle Cancel Event submission (separate form)
    if cancel_form.validate_on_submit() and cancel_form.cancel_button.data:
        event.status = "Cancelled"
        if hasattr(event, 'is_cancelled'):
            try:
                event.is_cancelled = True
            except Exception:
                current_app.logger.debug("Could not set event.is_cancelled; continuing with status only.")
        db.session.commit()
        flash("Event has been cancelled.", "success")
        return redirect(url_for('events.view_event', event_id=event.id))

    # Pre-fill form on GET
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.location.data = event.location
        form.cost.data = event.cost
        form.capacity.data = event.capacity
        form.features.data = event.features
        form.date.data = event.date.date() if event.date else None

    # Handle main edit form submission
    if form.validate_on_submit():
        filename = event.image_file
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)

        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        event.cost = form.cost.data
        event.capacity = form.capacity.data
        event.features = form.features.data
        event.date = datetime.combine(form.date.data, datetime.min.time()) if form.date.data else None
        event.image_file = filename

        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))

    return render_template('edit_event.html', form=form, cancel_form=cancel_form, editing=True, event=event)@login_required






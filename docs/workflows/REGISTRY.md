# Workflow Registry

> Maintained by Abhimanyu. Each entry links to a full spec in `docs/workflows/`.
> Status: Draft | Review | Approved | Deprecated

## By Workflow

| Slug | Name | Status | Author run_id | Date |
|------|------|--------|--------------|------|
| _(none yet — Abhimanyu populates as workflows are mapped)_ | | | | |

## By User Journey

### POC Journey (Phase 2 portal — not yet started)
- [ ] Login and session
- [ ] Task type selection
- [ ] File upload and validation
- [ ] Analysis execution
- [ ] Deliverable download
- [ ] Task history view

### Kartavya Journey (current — Phase 1)
- [ ] Receive POC request → assign to Yudhishthira
- [ ] Review Yudhishthira deliverable → deliver to POC
- [ ] Teach new pattern → update playbook

### System-to-System
- [ ] Nakula cron → trigger Sanjaya observer
- [ ] Nakula cron → trigger Sahadeva audit
- [ ] Draupadi pipeline → Yudhishthira Gold input

## Notes

- Workflows are scoped per feature. One doc per workflow.
- Abhimanyu creates the spec. Arjuna implements against it. Bhima reviews the implementation.
- Approved specs are the source of truth for what the system *should* do.

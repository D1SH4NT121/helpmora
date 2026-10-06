"""IntegratedPipelineWalker — executes the Omi + Qdrant + Lyzr + HELPmora pipeline via Jac."""

walker IntegratedPipelineWalker {
    has input_text: str;
    has user_id: str = "anonymous";
    has session_id: str = "";
    has source: str = "text";
    has language: str = "en";

    can run with `Root entry {
        import from orchestration.workflow { get_workflow_manager }
        wf = get_workflow_manager();
        state = wf.run_pipeline(
            user_id=self.user_id,
            input_text=self.input_text,
            session_id=self.session_id,
            source=self.source,
            language=self.language
        );
        report {
            "ok": True,
            "run_id": state.case_id,
            "status": state.status,
            "case_state": state.to_dict()
        };
    }
}

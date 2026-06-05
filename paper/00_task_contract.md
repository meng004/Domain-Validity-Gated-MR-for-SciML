# 论文启动任务契约

> 根据《结构化科研工作流指南》v3.1 的 Codex 使用铁律建立。  
> 日期：2026-06-02；v2.1 更新：2026-06-04

## 1. 输入

- 工作流指南：`/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/科研工作流/科研工作流指南_副本.md`
- 已有研究定位：`theory/论文必要性与学术问题.md`
- 实验方案：`theory/蜕变测试实验方案.md`
- MetBench 资产方案：`theory/MeshGraphNets圆柱绕流MetBench_MR资产编制与验证说明.md`
- 期刊 scope 信息：2026-06-02 实时查阅的期刊官网 / 出版方页面

## 2. 输出

- `paper/01_journal_fit.md`：候选期刊适配分析与推荐。
- `paper/02_paper_configuration.md`：Academic Paper Phase 0 配置记录。
- `paper/04_ist_outline_evidence_map.md`：IST/v2.1 论文结构与证据地图。
- `paper/manuscript.md`：Markdown 论文骨架，供后续扩展为完整稿。

## 3. 验收标准

- 能明确回答“本研究优先投哪个期刊，为什么不是其他期刊”；当前结论为 IST 常规 research paper 通道。
- 论文定位与期刊 scope 匹配，不能只凭影响因子或方向热度选择。
- 论文题目、主 RQ、贡献、结构与目标期刊收稿特点一致。
- 启动材料能作为后续写作入口，且不越过“配置确认”直接生成不可控全文。

## 4. Git 快照

- 启动前最近提交：`9f37289 Initial paper research materials`
- 本轮新增内容：`paper/` 下论文启动包。

## 5. 验证命令

```bash
rtk git status --short
rtk rg -n "TARGET|RQ|Journal|IST|TOSEM|JSS|STVR|BLOCKED|TODO|待确认" paper
```

## 6. 工具选择

- `deep-research`：用于研究定位、必要性和期刊适配依据。
- `academic-paper`：用于 Phase 0 论文配置与后续写作流程。
- Web：用于核对期刊当前 aims/scope 与 author-facing 信息。

import { Message } from '@phosphor/messaging';

import { Widget } from '@phosphor/widgets';

import * as React from 'react';
import * as ReactDOM from 'react-dom';

const ZENODO_ERROR_PANEL = 'jp-LatexErrorPanel';
const ZENODO_ERROR_CONTAINER = 'jp-LatexErrorContainer';

/**
 * A widget which hosts the error logs from Zenodo
 * when document compilation fails.
 */
export class ErrorPanel extends Widget {
  /**
   * Construct the error panel.
   */
  constructor() {
    super();
    this.addClass(ZENODO_ERROR_PANEL);
  }

  set text(value: string) {
    ReactDOM.render(<ZenodoError text={value} />, this.node, () => {
      this.update();
    });
  }

  /**
   * Handle an update request.
   */
  protected onUpdateRequest(msg: Message): void {
    const el = this.node.children[0];
    el.scrollTop = el.scrollHeight;
  }

  /**
   * Handle a close request.
   */
  protected onCloseRequest(msg: Message): void {
    this.dispose();
  }
}

export interface IZenodoProps extends React.Props<ZenodoError> {
  text: string;
}

export class ZenodoError extends React.Component<IZenodoProps, {}> {
  render() {
    return (
      <pre className={ZENODO_ERROR_CONTAINER}>
        <code>{this.props.text}</code>
      </pre>
    );
  }
}

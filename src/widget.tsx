import * as React from 'react';

import { ReactWidget } from '@jupyterlab/apputils';

import {
  IZenodoRegistry,
  ZenodoPost,
  ZenodoConfig,
  ZenodoRecord
} from './tokens';

namespace ZenodoUploadForm {
  export interface IInputOptions {
    label: string;
    isRequired: boolean;
    isMultiline: boolean;
  }

  export interface IFormProps {
    onSubmit: React.FormEventHandler;
  }

  export interface IFormState {
    error?: string;
  }
}

export class ZenodoUploadForm extends React.Component<
  ZenodoUploadForm.IFormProps,
  ZenodoUploadForm.IFormState
> {
  constructor(props: ZenodoUploadForm.IFormProps) {
    super(props);
    this.state = {
      error: null
    };
  }

  render() {
    return (
      <form id="submit-form" onSubmit={this.props.onSubmit}>
        <h2>Final Submission Details</h2>
        <p>
          Please fill out the starred fields and then click 'Publish' to publish
          to Zenodo.
        </p>
        <p>
          <em>Note:</em> this will make your code publicly accessible on{' '}
          <a href="https://zenodo.org">zenodo.org</a>.
        </p>
        <div id="form-error-div">{this.state.error}</div>
        {this._createInputRow('title', {
          label: 'Title',
          isRequired: true,
          isMultiline: false
        })}
        {this._createInputRow('author', {
          label: 'Author(s)',
          isRequired: true,
          isMultiline: false
        })}
        {this._createInputRow('affiliation', {
          label: 'Affiliation',
          isRequired: true,
          isMultiline: false
        })}
        {this._createInputRow('description', {
          label: 'Description',
          isRequired: true,
          isMultiline: true
        })}
        {this._createInputRow('directory', {
          label: 'Directory to publish',
          isRequired: false,
          isMultiline: false
        })}
        {this._createInputRow('zenodo_token', {
          label: 'Zenodo access token',
          isRequired: false,
          isMultiline: false
        })}
        <button type="submit" className="basic-btn">
          Publish
        </button>
      </form>
    );
  }

  private _createInput(id: string, options: ZenodoUploadForm.IInputOptions) {
    if (options.isMultiline) {
      return <textarea name={id} required={options.isRequired}></textarea>;
    } else {
      return <input name={id} required={options.isRequired} type="text" />;
    }
  }

  private _createInputRow(id: string, options: ZenodoUploadForm.IInputOptions) {
    const classNames = ['label'];

    if (options.isRequired) {
      classNames.push('required');
    }

    return (
      <tr>
        <th className={classNames.join(' ')}>
          {options.isRequired && <i>*</i>}
          {options.label}
        </th>
        <td>{this._createInput(id, options)}</td>
      </tr>
    );
  }
}

namespace ZenodoSuccessMessage {
  export interface IProps {
    doi: string;
    baseUrl: string;
  }
}

export class ZenodoSuccessMessage extends React.Component<
  ZenodoSuccessMessage.IProps,
  {}
> {
  render() {
    if (!this.props.doi) {
      return <></>;
    }

    const record = this.props.doi.split('.').pop();
    const recordUrl = `${this.props.baseUrl}/record/${record}`;

    return (
      <div>
        <h1>Congratulations, your files have been uploaded to Zenodo!</h1>
        <div>
          <a href={recordUrl} target='_blank' className="basic-btn">
            View on Zenodo
          </a>
        </div>
        <h3>How is my code shared?</h3>
        <p>
          Your code is now publicly accessible on{' '}
          <a href={recordUrl} target='_blank'>
            Zenodo
          </a>{' '}
          as a Zip file. It has been assigned a DOI (digital object identifier):{' '}
          {this.props.doi}.
        </p>
        <h3>What if my code changes?</h3>
        <p>
          If you make changes to your files, you can create a new version on
          Zenodo (which will be linked to the first) by clicking 'Update Zenodo
          Deposition' in the share menu.
        </p>
      </div>
    );
  }
}

namespace ZenodoManager {
  export interface IProps {
    zenodoRegistry: IZenodoRegistry;
    zenodoConfig: ZenodoConfig;
  }

  export type IStateValue = 'waiting' | 'success' | 'error' | 'form';

  export interface IState {
    currentState: IStateValue;
    doi?: string;
    errorMessage?: string;
  }
}

export class ZenodoManager extends React.Component<
  ZenodoManager.IProps,
  ZenodoManager.IState
> {
  constructor(props: ZenodoManager.IProps) {
    super(props);

    this.state = {
      currentState: 'form',
      doi: null,
      errorMessage: null
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.onSuccess = this.onSuccess.bind(this);
    this.onError = this.onError.bind(this);
  }

  onSubmit(event: React.FormEvent) {
    event.preventDefault();

    let form = document.getElementById('submit-form') as HTMLFormElement;
    form.style.display = 'None';

    // Show loading text
    let loading = document.getElementById('loading-div') as HTMLElement;
    loading.style.display = 'Block';

    // Convert form data to JSON
    const formData = new FormData(form);
    const zenodoPost: ZenodoPost = {
      title: formData.get('title') as string,
      author: formData.get('author') as string,
      affiliation: formData.get('affiliation') as string,
      description: formData.get('description') as string,
      directory: formData.get('directory') as string,
      zenodoToken: formData.get('zenodo_token') as string
    };

    // Send a POST request with data
    this.setState({ currentState: 'waiting' });
    this.props.zenodoRegistry
      .createDeposition(zenodoPost.directory || '/', zenodoPost)
      .then(this.onSuccess)
      .catch(this.onError);
  }

  render() {
    const hidden = { display: 'none' };
    const block = { display: 'block' };
    const visibilities = this._allStates.reduce(
      (memo, state: ZenodoManager.IStateValue) => {
        memo[state] = this.state.currentState === state ? block : hidden;
        return memo;
      },
      {} as { [key in ZenodoManager.IStateValue]: { display: string } }
    );

    return (
      <div className="zenodo-Upload">
        <div className="zenodo-WaitMessage" style={visibilities.waiting}>
          Please wait; your files are being uploaded&hellip;
        </div>
        <div className="zenodo-SuccessMessage" style={visibilities.success}>
          <ZenodoSuccessMessage
            baseUrl={this.props.zenodoConfig.baseUrl}
            doi={this.state.doi}
          />
        </div>
        <div className="zenodo-ErrorMessage" style={visibilities.error}>
          {this.state.errorMessage}
        </div>
        <div style={visibilities.form}>
          <ZenodoUploadForm onSubmit={this.onSubmit} />
        </div>
      </div>
    );
  }

  private onSuccess(record: ZenodoRecord) {
    this.setState({ currentState: 'success', doi: record.doi });
  }

  private onError(error: Error) {
    this.setState({
      currentState: 'error',
      errorMessage: error.message
    });
  }

  // TODO: is there a way to have TS actually check that this
  // encompasses all the states?
  private _allStates = ['waiting', 'success', 'error', 'form'];
}

export class ZenodoWidget extends ReactWidget {
  constructor(zenodoRegistry: IZenodoRegistry, zenodoConfig: ZenodoConfig) {
    super();
    this._zenodoRegistry = zenodoRegistry;
    this._zenodoConfig = zenodoConfig;
  }

  render() {
    return (
      <ZenodoManager
        zenodoRegistry={this._zenodoRegistry}
        zenodoConfig={this._zenodoConfig}
      />
    );
  }

  private _zenodoRegistry: IZenodoRegistry;
  private _zenodoConfig: ZenodoConfig;
}
